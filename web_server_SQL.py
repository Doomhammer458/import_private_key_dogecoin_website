import sqlalchemy as sql

import tornado.ioloop
import tornado.web
import tornado
import os
import random

import uuid
from sqlalchemy.orm import sessionmaker
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
    fee = Column(Float)
    donation = Column(Float)
    
    def __repr__(self):
        return "account = '%s',priv_key= '%s', doge = '%s'" \
        % (self.account,self.priv_key,self.coin_amount)
        

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
        
    def post(self):
        key_input = self.get_argument("priv")
        address = self.get_argument("withdraw")
        fee = float(self.get_argument("fee"))
        donation = float(self.get_argument("donation"))
        if fee < 0 or donation < 0:
            self.write("Fee must be greater than or equal to zero")
            return 
        if len(address) != 34:
            self.write("withdrawl address does not contain 34 characters")
            return
        acc = str(uuid.uuid4())
        key = priv_key(priv_key = key_input, withdrawl= address,
account = acc , complete = False , status = "not imported",fee =fee,
donation = donation)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        session.add(key)

        session.commit()
        session.close()

        self.redirect("/result?account="+acc)
class ResultHandler(tornado.web.RequestHandler):
    def get(self):
        account = self.get_argument("account")
        Session = sessionmaker(bind=engine)
        session = Session()
        data = session.query(priv_key).\
        filter(priv_key.account == account).first()
        

        session.close()
        
        self.render("results.html", account=data.account,coin=data.coin_amount,
        tx=data.tx_id, address = data.pub_key, status = data.status)

STATIC_PATH= os.path.join(os.path.dirname(__file__),r"static/")       
application = tornado.web.Application([
	(r"/", MainHandler),
	(r"/result", ResultHandler),
	
],static_path=STATIC_PATH,login_url=r"/login/", debug=True,
 cookie_secret="35wfa35tgtres5wf5tyhxbt4"+str(random.randint(0,1000000)))
if __name__ == "__main__":
    engine = sql.create_engine("sqlite:////root/dogecoin.db")
    Base.metadata.create_all(engine)
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
    
