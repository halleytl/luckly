#-*-coding:u8
import torndb
from __init__ import BaseEngine


class Engine(BaseEngine):
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.host = self.kwargs.get("host", "127.0.0.1" )
        self.port = self.kwargs.get("port", "3306")
        self.db = self.kwargs.get("db") 
        self.user = self.kwargs.get("user")
        self.password = self.kwargs.get("password")
                
    def get_conn(self):
        return torndb.Connection(
            self.host+":" +self.port,
            self.db,
            user=self.user,
            password=self.password)

    def param_format(self, **params):
        """
        [库 ]__[表]__[字段]__[操作]
        如果__ 开头为默认库
        单下划线开头为特殊命令
        """
        querys = []
        st = {}
        for k in params:
            if len(k.split("__")) == 4:
                db, table, key, op =  k.split("__")
            elif len(k.split("__")) == 3:
                db, table, key =  k.split("__")
                op = "eq"
            value = params[k][0]
            st["%s__%s" % (table, key)]= {"op":op, "value":value}
            querys.append("%s.%s.%s" %(self.db if db else db, table, key))
        key_struct = self._struct(querys)
        return { k: operator_format(op, value, key_type=key_struct[k]) for k in st}

    def show(self, inf_name, **params):
        """
        show/shop/brand_info?__ecs_business_info__business_id__in=1,2,3
        show/shop/brand_info?__ecs_business_info__business_id__in=1,2,3
        """

        #print torndb.MySQLdb.escape_string(data) 
        res = open(inf_name + ".sql").read().format(**self.param_format(**params))
        return res

    def search(self, inf_name, **params):
        sql = self.show(inf_name , **params)
        return self.get_conn().query(sql)

    def _struct(self, querys, show_type=None):
        if not show_type :
            res = {}
            for query in querys:
                db, table, key = query.strip().split(".")
                sql = "show FULL COLUMNS from {db}.{table} where Field='{key}'".format(db=db,table=table,key=key)
                r = self.get_conn().query(sql)
                if r:
                    res["%s__%s" % (table, r[0]["Field"])] = get_type(r[0]["Type"])

        else:
            res = []
            for query in querys:
                db, table, key = query.strip().split(".")
                sql = "show FULL COLUMNS from {db}.{table} where Field='{key}'".format(db=db,table=table,key=key)
                r = self.get_conn().query(sql)
                if r: 
                    res.append(r[0]) 
        return res

    def struct(self, show_type=None, **kwargs):
        querys = kwargs.get("search")
        return self._struct(querys, show_type)

def operator_format(op, value, key_type="none", con_type="mysql"):
    """
    #[数据表]__[字段]
    #[数据表]__[字段]__[操作关系]
    #[数据表]__[字段]__[操作关系]__[数据类型]
    根据
    default: = 
    gt: >=
    lt: <=
    neq: !=
    in: in ()
    not in: not in ()
    like: like "%xxx%"
    """
    operators = {
        "eq": "= %s",
        "neq": "!= %s",
        "gt": ">= %s",
        "lt": "<= %s",
        "in": "in (%s)",
        "not_in": "not in (%s)",
        "like": "%%%s%%",
        #"not_in_sql"
    }
    return "{op}".format(op=operators[op] % (data_format(value, key_type)))

def data_format(value, key_type):
    """

    """
    if key_type == "string":
        # string , data
        return ",".join(map(lambda x: '"' + x + '"', torndb.MySQLdb.escape_string(value).split(",")))
    else:
        # int,
        return value


def get_type(key_type):
    if "int" in key_type:
        return "int"
    elif "varchar" in key_type:
        return "string"
    else:
        return key_type

    

