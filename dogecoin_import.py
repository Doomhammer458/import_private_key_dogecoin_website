import sqlalchemy as sql
engine = sql.create_engine("mysql://doge:dogecoin@localhost/dogecoin")
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
from sqlalchemy import Column, String,Float, Boolean 
class priv_key(Base):
    __tablename__ = "priv_key"
    priv_key = Column(String(55))
    account = Column(String(50),primary_key=True)
    pub_key = Column(String(50))
    coin_amount = Column(Float)
    status = Column(String(50))
    complete = Column(Boolean)
    tx_id = Column(String(100))
    withdrawl = Column(String(50))
    def __repr__(self):
        return "account = '%s',priv_key= '%s', doge = '%s'" \
        % (self.account,self.priv_key,self.coin_amount)
        
import dogecoinrpc as doge
import time
doge_conn = doge.connect_to_local()
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

for instance in session.query(priv_key).filter(priv_key.complete==False):
    
    try:
        doge_conn.importprivkey(instance.priv_key,instance.account)
    except:
        print "rescanning"
        time.sleep(1)
        print "rescanning"
        time.sleep(400)
    print "scan complete"
    doge_conn = doge.connect_to_local()
    instance.pub_key = doge_conn.getaddressesbyaccount(instance.account)[0]
    instance.coin_amount = doge_conn.getbalance(account=instance.account)
    instance.tx_id = doge_conn.sendfrom(instance.account,instance.withdrawl,float(str(instance.coin_amount -1)))
    print instance
    instance.status = "complete"
    instance.complete = True
    session.add(instance)
    session.commit()
    
session.close()
