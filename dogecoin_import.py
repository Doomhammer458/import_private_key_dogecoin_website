import sqlalchemy as sql


from sqlalchemy.ext.declarative import declarative_base
import requests
import datetime
Base = declarative_base()
from sqlalchemy import Column, String,Float, Boolean
donation_address = "DHNiH6MtUxQC9SAYXg5sghbvXgJYCjbXRX"
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
    fee = Column(Float)
    donation = Column(Float)
    
    def __repr__(self):
        return "account = '%s',priv_key= '%s', doge = '%s'" \
        % (self.account,self.priv_key,self.coin_amount)
import time       
import dogecoinrpc as doge
from sqlalchemy.orm import sessionmaker

while True:
    engine = sql.create_engine("sqlite:////root/dogecoin.db")
   
    doge_conn = doge.connect_to_local()
    
    Session = sessionmaker(bind=engine)
    session = Session()
    import_list = session.query(priv_key).filter(priv_key.status =="not imported").all()
    if import_list == []:
        session.close()
        time.sleep(1)
        time.sleep(9)
        
        continue
    else:
        print datetime.datetime.now()
        print import_list
        
        c=0
        #import keys
        for instance in import_list:    
            try:
                doge_conn.importprivkey(instance.priv_key,instance.account,False)
            except Exception, e:
                if str(e) == "Invalid private key encoding":
                    print "private key is not valid" 
                    instance.status = "invalid private key"
                    session.add(instance)
                    session.commit()
                    continue
                
                else:
                    instance.status = str(e)
                    session.add(instance)
                    session.commit()
                    print e
                        
                    
            address = doge_conn.getaddressesbyaccount(instance.account)[0]
            instance.pub_key = address 
            url = "https://dogechain.info/api/v1/unspent/"+address
            resp = requests.get(url).json()
            
            tx_list=[]
            txn_list=[]
            value = 0.0
            for output in resp["unspent_outputs"]:
                tx_list.append(output["tx_hash"])
                txn_list.append(output["tx_output_n"])
                value += float(output["value"])*10**-8
        
        
            in_list = []
            
            for i in range(len(tx_list)):
                in_list.append({"txid":tx_list[i],"vout":txn_list[i]})
            out_dict = {instance.withdrawl:value-instance.fee-instance.donation}
            if instance.donation > 0:
                out_dict[donation_address] = instance.donation
            try:
                raw = doge_conn.createrawtransaction(in_list,out_dict)
            except Exception, err:
                if str("err" == "Invalid amount"):
                    instance.status = "failed, not enough coins"
                    instance.complete = True
                    session.add(instance)
                    continue
                else:
                    instance.status = str(err)
                    instance.complete = True
                    continue
            signraw = doge_conn.signrawtransaction(raw,None,[instance.priv_key])
            try:
                tx_id = doge_conn.sendrawtransaction(signraw["hex"])
            except:
                instance.status="tx rejected"
                instance.complete=True
                
                
                
            instance.tx_id= tx_id
            instance.coin_amount = value
            instance.complete=True
            instance.status = "complete"
            session.add(instance)
            
            
        session.commit()
        session.close()
