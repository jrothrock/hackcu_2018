from functools import partial
import wst.core.gromit as gromit
from   wst.ui.application import SimpleApp, SimpleAppView, SimpleAppController
from   wst.ui.controls import Button, Label, TextField, IFrame
from   wst.ui.layout import Col, Row, VList
import datetime
from wst.ts.tsfns import ts_object
from wst.lib.tenor import ContractTenor
from wst.core.analytics import bs
import scipy.stats
import numpy
import math
from mpl_toolkits.mplot3d import axes3d
import matplotlib.pyplot as plt
from matplotlib import cm
# Shit Code, BSM returns zero. Shall check later

# We follow the MVC pattern to define a complete application in python. The platform has a special
# dependency graph framework that we use to make applications reactive without too much code. If
# you run this app and see what it does first, then look at how its constructed. You should be able
# to get a reasonably functional web app without writing and javascript/css/html, however if you
# web dev skills you can certainly make the app nicer if you like.

volatilities = []
prices = []
strike_prices = []

def show_view(model, name):
    model.target_url.set_value(name)  

class ViewModel(gromit.Object):
    @gromit.fn(gromit.CanSet)
    def target_url(self):
        return "./#/stock"    
    
class Model(gromit.Object):
    '''Model class for the calculator. 
    
    Implement the model (back end) of the application. The model has two inputs fields with a
    special decorator and and output field which the same decorator with different settings.
    
    You can see from playing with the app that when you type into the inputs the Sum function
    runs and the new value gets pushed into the view. This is magically happening in part due
    to the decorators below. Understanding these graph is an advanced topic, for now its 
    sufficient to note that something interesting is happening which can be used to create
    reactive behavior, but there are some caveats.   
    '''
    
    @gromit.fn(gromit.Stored)
    def Input1(self):
        return 'Energy/CMECLopts'
    
    def getVolitility(self,call,strike_price,price,exp,today):
        
        print(call)
        print(strike_price)
        print(price)
        
        is_call  = call
    
        spot     = int(price * 100)
        strike   = int(strike_price * 100)
       # exp_date = datetime.date(2018, 7, 31)
        today    = datetime.date(2018, 2, 20)
        texp     = texp = (exp - today).days / 365.

        print(spot)
        print(strike)
        
        try:            
            vol      = bs.imp_vol(
                is_call,
                spot,
                strike,
                texp,
                0,
                0,
                697
            )
        except:
            return False
        
        print('Volatility:', vol)
        return vol
    
    def checkCallPrice(self,price, mean, std, strike_price, exp):
        today    = datetime.date(2018, 2, 20)
        dtm = (exp - today).days / 365.
        d = (numpy.log(price / strike_price) + ((0.03 + std/2) * dtm)) / (std*numpy.sqrt(dtm))
        d_two = (numpy.log(price / strike_price) + ((0.03 - std/2) * dtm)) / (std*numpy.sqrt(dtm))
        bsm = price * (scipy.stats.norm(mean, std).pdf(d)) - (price * math.exp(-0.03*dtm) * scipy.stats.norm(mean,std).pdf(d_two))
        print(bsm)
        
    def checkPutPrice(self, price,  mean, std, strike_price, exp):
        today    = datetime.date(2018, 2, 20)
        dtm = (exp - today).days / 365.
        d = (numpy.log(price / strike_price) + ((0.03 + std/2) * dtm)) / (std*numpy.sqrt(dtm))
        d_two = (numpy.log(price / strike_price) + ((0.03 - std/2) * dtm)) / (std*numpy.sqrt(dtm))
        bsm = (price * math.exp(-0.03*dtm)* scipy.stats.norm(mean,std).pdf(d_two * -1)) - price * (scipy.stats.norm(mean, std).pdf(d * -1))
        print(bsm)
        
    def calcStockStuff(self):
        market_object = gromit.ns['/Assets/Energy/CME CL']
    
        # Lets try and get the prices for this future. If you were to click on 'Settlements' from the web page
        # you will see a table which the contract months that are available and the settlement prices in the 
        # column 'Settle'. You can move the date dropdown to go back time.

        # The prices are stored in a time series, which is an ordered dictionary of date, curve pairs.
        # We can select a day's price (if the data is there) using some handy function calls.

        market_date   = datetime.date(2018, 2, 21)
        price_ts      = ts_object(gromit.ns, 'Energy/CMECLfuts')
        price_curve   = price_ts.Value(market_date)

        print('Prices:', price_curve)    

        #Note that only valid days in the past will work when asking for data. The data you see shoud
        #match what you see on the Nymex website. So now you have the underlying prices for a market.
        #To get to the option prices you'll need a companion time series
        # Energy/CMECLopts
        
        opt_ts       = ts_object(gromit.ns, self.Input1())
        option_curve = opt_ts.Value(market_date)

        print('Option prices:', option_curve)

        # The format of the option data is (is_call, strike, option price). Recall that given these things
         #plus some additional information and our BS function we can turn this information into a volatility

        # Aside from printing these python objects, what other functionality do they have? After executing
        # this script it puts the local variables into the IPython shell. You can ask the objects for 
        # their type (ex. type(market_objet)). That should print out the module name which will be in a folder
        # /wst/mktint/nrgfut.py (see the left tree)

        # In that module (and base classes) will be a lot of useful functionality. One thing that we need to
        # find is when do options expire. Handily
        
        exp_code = ContractTenor('Dec18')
        exp_date = market_object.ExpirationDate(exp_code)

        print('Expiration:', exp_date)
        
        print(type(option_curve))
        method_list = [func for func in dir(option_curve) if callable(getattr(option_curve, func))]
        print(method_list)
        print(option_curve.values())
            
        # shit code is shit code
            
        values = option_curve.values()
        dates = option_curve.tenors()
        price_curve = price_curve.values()   
        new_dates = []
        global strike_prices
        global prices
        global volatilities
        for index,i in enumerate(values):
            for x in i:
               volatility = self.getVolitility(x[0],float(x[1]),float(x[2]),datetime.datetime.strptime(str(dates[index]),'%b%y').date(),'test')
               print(volatility)
               print('vol')
               if(volatility != False and volatility != None):
                  volatilities.append(volatility)
                  prices.append(price_curve[index])
                  strike_prices.append(x[1])
                  new_dates.append(datetime.datetime.strptime(str(dates[index]),'%b%y').date())
            
        mean = sum(prices) 
        std = numpy.std(prices)   
        print('here')
        print(strike_prices)
        for index,volatility in enumerate(volatilities):
            if volatility != False:
                if x[0]:
                    try:
                        self.checkCallPrice(prices[index], mean, std, strike_prices[index], new_dates[index])
                    except:
                        print('fail')
                else:
                    try:
                        self.checkPutPrice(prices[index], mean, std, strike_prices[index], new_dates[index])
                    except:
                        print('fail')
    
class AppController(SimpleAppController):
    '''
    The controller is the part of the mvc framework that connects the model and the view. This where you would put things like
    action to operate when buttons are clicked.
    
    '''
    
    def __init__(self, model):
        self.model = model
        
        
    def getStockStuff(self):
        print("ran")
        stock_stuff = self.model.calcStockStuff()
        return stock_stuff
            

#
# The last part of the puzzle is the view. This is simply a representation of the view where the layout id described in python objects.
#
# There is a main wiki page for UI in general (https://wst.wsq.io/wst/wiki/training/gromit-simple)
#
# But I suggest you concentrate on the the bits that are crucial:
#
# What are all the widgets and how do I lay them out (the bits under Components overview)
# And even better sume examples
#
# wst/ui/examples/* (not everything in there will run, so ignore what does not)
#
# But let me draw your attention to:
#
# wst/ui/examples/app_controls.py - best way to see what you have in your tool bag (see 06 to fully digest the code)
# wst/ui/examples/app_chart_* - 
# wst/ui/examples/app_spreadsheet_*
#
# Please ignore anything that has to do with 'glint' which is an under-development next version of ui UI plantform
#

def volatility_plot(model):
    
    #We use matplotlib to to generate a chart. This is a popular python package.
    global prices
    global volatilities
    model.calcStockStuff()
    min_price = min(prices)
    max_price = max(prices)
    min_vol = min(volatilities)
    max_vol = max(volatilities)
    fig = plt.figure()
   # X, Y, Z = axes3d.get_test_data(0.05)
   # ax.plot_surface(X, Y, rstride=8, cstride=8, alpha=0.3)
        
#    for index,price in enumerate(Model.prices):
#        cset = ax.contour(X, Y, 
    
#    cset = ax.contour(X, Y, Z, zdir='z', offset=-100, cmap=cm.coolwarm)
#    cset = ax.contour(X, Y, Z, zdir='x', offset=-40, cmap=cm.coolwarm)
#    cset = ax.contour(X, Y, Z, zdir='y', offset=40, cmap=cm.coolwarm)

    plt.plot(prices, volatilities)
    plt.ylabel('Volatility')
    plt.xlabel('Strike Price')
   # ax.set_xlabel('Strike')
   # ax.set_xlim(min_price, max_price)
   # ax.set_ylabel('Implied Volatility')
   # ax.set_ylim(min_vol, max_vol)

    #Unfortunately you can't see it in your browser, the package shows the image on the remote machine
    #in amazon
    plt.show()
    
    #But we can create a temporary image and embed it directly into an html page
    plt.savefig('temp.png')
    import base64
    data_uri = base64.b64encode(open('temp.png', 'rb').read()).decode('utf-8').replace('\n','')
    img_tag = '<img src="data:image/png;base64,{0}">'.format(data_uri)
    html = '<html>Volatility<b>%s<b></html>' % img_tag

    return html

def pl_plot():
        
    #We use matplotlib to to generate a chart. This is a popular python package.
    html = '<html>P&L<b>Footer<b></html>'

    return html

def greeks_plot(model):
        
    #We use matplotlib to to generate a chart. This is a popular python package.
    global strike_prices
    global prices
    model.calcStockStuff()
    min_price = min(strike_prices)
    max_price = max(strike_prices)
    min_vol = min(prices)
    max_vol = max(prices)
    plt.plot(strike_prices, prices)
    plt.ylabel('Asset Price')
    plt.xlabel('Strike Price')

    #Unfortunately you can't see it in your browser, the package shows the image on the remote machine
    #in amazon
    plt.show()
    
    #But we can create a temporary image and embed it directly into an html page
    plt.savefig('delta_temp.png')
    import base64
    delta_data_uri = base64.b64encode(open('delta_temp.png', 'rb').read()).decode('utf-8').replace('\n','')
    delta_img_tag = '<img src="data:image/png;base64,{0}">'.format(delta_data_uri)
    html = '<html>Greeks<b>Delta%s<b></html>' % delta_img_tag

    return html

class MainView(SimpleAppView):
    def __init__(self,model):
        content = VList([
            '<h2>Volatility, P&L, and the Greeks</h2>',
            Button('Stock', on_click=partial(show_view, model, './#/stock')),
            Button('Volatility', on_click=partial(show_view, model, './#/volatility')),
            Button('P&L', on_click=partial(show_view, model, './#/pl')),
            Button('Greeks', on_click=partial(show_view, model, './#/greeks')),
            
            #We can embed html content directly into an IFrame
            IFrame(src=model.target_url, css_style="height: 800px;max-width:100vw;"),
            volatility_view
        ])
        super().__init__(content, view_name="index")

class StockView(SimpleAppView):
    def __init__(self,model,inner_model,controller):
        content = [
            Row([
                Col(size=3, content=Label('Stock Price:')),
                Col(size=3, content=TextField(inner_model.Input1)),
                Col(size=6, content=Button('Calculate', on_click=controller.getStockStuff)),
            ]),
        ]
        super().__init__(content, view_name="stock") 

        
        
def volatility_view(model):
    html = volatility_plot(model)
    
    return html  

def pl_view():
    html = pl_plot()
    
    return html  

def greeks_view(model):
    html = greeks_plot(model)
    
    return html  
        
class VolatilityView(SimpleAppView):
    def __init__(self,model,inner_model,controller):
        content = [
            volatility_view(inner_model)
        ]
        super().__init__(content, view_name='volatility')
        
class PLView(SimpleAppView):
    def __init__(self,model,inner_model,controller):
        content = [
            pl_view()
        ]
        super().__init__(content, view_name='pl')

        
class GreeksView(SimpleAppView):
    def __init__(self,model,inner_model,controller):
        content = [
            greeks_view(inner_model)
        ]
        super().__init__(content, view_name='greeks')



def main():
    
    # Here is where the model, controller and view are instantiated and then they launch an async web page
    
    model = ViewModel()
    inner_model      = gromit.ns.new(Model)
    
    controller = AppController(inner_model)
    #app_views  = create_views(controller)
    
    app = SimpleApp(views=[
            MainView(model),
            StockView(model,inner_model,controller),
            VolatilityView(model,inner_model,controller), 
            PLView(model,inner_model,controller),
            GreeksView(model,inner_model,controller)
        ],
        title="Volitiliy Calculator",
        app_style="fluid-nohome-nofooter", 
        show_db=False
    )
    app.run()
    
    return controller

    
if __name__ == '__main__':
    
    # While the app is running you can still use the IPython shell. With a reference to the controller you can
    # do things like inspecting your model to make sure it's doing what you want
    
    # ex. controller.model.Sum() should show you the same number on screen
    # and if you were to do something like call
    # controler.model.Input1.set_value(20) you should see you UI updates
    #
    
    controller = main()