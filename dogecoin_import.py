import sqlalchemy as sql
engine = sql.create_engine("mysql://doge:dogecoin@localhost/dogecoin")
from sqlalchemy.ext.declarative import declarative_base
import requests
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
import_list = session.query(priv_key).filter(priv_key.status =="not imported").all()
print import_list
c=0
for instance in import_list:
    if c ==len(import_list)-1:
        
        try:
            doge_conn.importprivkey(instance.priv_key,instance.account)
        except Exception, e:
            if str(e) == "Invalid private key encoding":
                print "private key is not valid" 
                instance.status = "invalid private key"
                session.add(instance)
                session.commit()
                continue
            
            elif str(e) == "timed out":
                print "rescanning"
                instance.status = "importing"
                session.add(instance)
                session.commit()
                time.sleep(1)
                time.sleep(400)
            else:
                instance.status = str(e)
                session.add(instance)
                session.commit()
                print e
                
            
            
    else:
         try:
            doge_conn.importprivkey(instance.priv_key,instance.account)
            instance.status = "importing"
            session.add(instance)
            session.commit()
         except Exception, e:
            if str(e) == "Invalid private key encoding":
                print "private key is not valid" 
                instance.status = "invalid private key"
                session.add(instance)
                session.commit()                
                
                continue
    c+=1 
print "scan complete"

import_list = session.query(priv_key).filter(priv_key.status =="importing").all()

for instance in import_list:
    try:
        doge_conn = doge.connect_to_local()
       
        instance.pub_key = doge_conn.getaddressesbyaccount(instance.account)[0]

        url = "https://dogechain.info/api/v1/address/balance/" + str(instance.pub_key)
        #print url
        res = requests.get(url)
        res_dict = res.json()
        instance.coin_amount = float(res_dict["balance"])
        
        print instance.coin_amount
        
        instance.tx_id = doge_conn.sendfrom(instance.account,instance.withdrawl,float(str(instance.coin_amount -1)))
        
        instance.status = "complete"
        instance.complete = True
    except Exception, err:
        instance.status = "error:"+str(err)
        print err
    print instance
    session.add(instance)
    session.commit()
    
    
session.commit()
session.close()
