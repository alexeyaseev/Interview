import onetick.py as otp
from sol.common.py.fix.otq.constructors.Constructor import Constructor
from datetime import datetime
import logging
import onetick.query as otq


class DataLoadPositionsInstinet(Constructor):
    log = logging.getLogger(__name__)

    def __init__(self, source: otp.Source, date: datetime.date):
        DataLoadPositionsInstinet.log.info('Loading the positions file')
        self._source = source
        self._date = date.strftime('%Y%m%d')

    def construct(self) -> otp.Source:
        src = self._source
        schema = {"SYMBOL": str,
                  "INSTRTYPE": str,
                  "EXCHID": str,
                  }
        src.schema.set(**schema)
        src['EXCHID'] = src.apply(
            lambda row: "OPRA" if (row['INSTRTYPE'] == "O" and row["EXCHID"] == "UNK") else row['EXCHID'])
        src['__PRODUCT_CODE'] = src["SYMBOL"]
        src['__PRODUCT_CODE'] = src.apply(self.get_product_code)
        src['__STRIKE_EXPIRY'] = src.apply(
            lambda row: row['SYMBOL'].str.substr(row["SYMBOL"].str.len() - 15) if
            row["INSTRTYPE"] == "O" and row["EXCHID"] in ("OPRA", "XCBO")
            else ""
        )
        src['__SYMBOL_FOR_MAPPING'] = src.apply(self.get_symbol_for_mapping)
        src['__ROOT_SYMBOL'] = src.apply(self.get_root_symbol)
        src = self._throw(src)
        return src

    @staticmethod
    def get_product_code(row):
        """
        options are provided in the format SPX221216P02050000 or SPXW221216C02050000
        we need to get the product code as SPX/SPXW by substracting 15 chars from the end(8 chars for the strike price
        1 char for type and 6 chars for the expiry date)
        """
        if row["INSTRTYPE"] == "O" and row["EXCHID"] in ("OPRA", "XCBO"):
            return row["SYMBOL"].str.substr(0, row["SYMBOL"].str.len() - 15)
        else:
            return row["SYMBOL"]

    @staticmethod
    def get_symbol_for_mapping(row):
        """
        abc
        def
        """
        if row["INSTRTYPE"] == "O" and row["EXCHID"] in ("OPRA", "XCBO"):
            return row["__PRODUCT_CODE"] + " " * (6 - row["__PRODUCT_CODE"].str.len()) + row["__STRIKE_EXPIRY"]
        elif row["INSTRTYPE"] == "E":
            return row["SYMBOL"].str.replace(".", "")
        else:
            return row["SYMBOL"]

    @staticmethod
    def get_root_symbol(row):
        """
        we need to get root symbol for pat_speedup_search parameter
        it will be ticker for equities, extracted PRODUCT_CODE for options of CME (and all its floors)
        and the whole symbol for options of OPRA and XCBO
        Samples (INSTRTYPE, SYMBOL) -> __ROOT_SYMBOL
        XCBO, OPRA: Option, SPX123213P123123 -> SPX   123213P123123
        XCME, XNYM, XCEC, XCBT, XMGE: Option, AAOG3 C7800  -> AAO (same logic on every CME floors)
        """
        if row["INSTRTYPE"] == "O" and row["EXCHID"] in ("OPRA", "XCBO"):
            return row["__PRODUCT_CODE"] + " " * (6 - row["__PRODUCT_CODE"].str.len()) + row["__STRIKE_EXPIRY"]
        elif row["INSTRTYPE"] == "E":
            return row["SYMBOL"].str.replace(".", "")
        else:
            return row["SYMBOL"]

    @staticmethod
    def _throw(src):
        src.sink(otq.Throw(where="EXCHID != 'XNYM' and EXCHID != 'XCME' and EXCHID != 'XCBT' and EXCHID != 'XCEC' "
                                 "and EXCHID != 'XMGE' and EXCHID != 'XCBO' and EXCHID != 'OPRA' and EXCHID != 'XNAS'"
                                 "and EXCHID != 'BATO' and EXCHID != 'OTC' and EXCHID != 'XNYS'"
                                 "and EXCHID != 'IFED' and EXCHID != 'NDEX'",
                           message="EXCHID field has an unexpected value"))
        return src
