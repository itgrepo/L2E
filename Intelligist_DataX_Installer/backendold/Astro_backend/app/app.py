from ServiceConfig import *
from ServiceConfig.register import *
from ServiceConfig.bigdataservice import *
from ServiceConfig.login import *
from ServiceConfig.group_service import *
from ServiceConfig.access_service import *
from ServiceConfig.organization_service import *
from ServiceConfig.category_service import *
from ServiceConfig.site_config import *
from Management import *
from Management.groupMgmt import *
from Management.rolesMgmt import *
from Management.usersMgmt import *
from Security import *
from Security.consent import *


@app.route('/')
def hello():
    return "Hello World!"

if __name__ == '__main__':

    # context = ('ssl/internal.databureau.set.crt', 'ssl/internal.databureau.set.key')
    # app.run(debug=True,host='0.0.0.0',ssl_context=context,threaded=True,port=5000)
	app.run(debug=True, host='0.0.0.0',port=7000, threaded = True)
