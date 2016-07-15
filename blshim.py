import base64, json
import BLcred
from petlib.bn import Bn
from petlib.ec import EcGroup, EcPt

params = BLcred.BL_setup()
(G, q, g, h, z, hs) = params
issuer_state = None

############################################################################################
# Helper routines to serialise, deserialise tuples containing EcPt, Bn...
# Extend json to serialise/deserialise EcPt, as per https://docs.python.org/3/library/json.html. 
# Notes:
# 1. Json has no concept of python tuples. Tuples are therefore serialised as json lists;
#    the deserialiser assumes all json lists should be turned back into tuples
# 2. These routines need G - hence the ordering & inclusion in this file
class petlibEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, EcPt):
            return {"EcPt:": base64.urlsafe_b64encode(obj.export())}
        if isinstance(obj, Bn):
            return {"Bn:": base64.urlsafe_b64encode(obj.binary())}            
        return json.JSONEncoder.default(self, obj)
 
def as_petlib2(dct):
    if 'EcPt:' in dct:
        binary = base64.urlsafe_b64decode(str(dct['EcPt:']))
        return EcPt.from_binary(binary, G)
    if 'Bn:' in dct:
        binary = base64.urlsafe_b64decode(str(dct['Bn:']))
        return Bn.from_binary(binary)            
    return dct 

def tuplify(listything):
    if isinstance(listything, list): return tuple(map(tuplify, listything))
    if isinstance(listything, dict): return {k:tuplify(v) for k,v in listything.items()}
    return listything
    
def serialise(t):
    s = json.dumps(t, separators=(',', ':'),cls=petlibEncoder)
    return s

    
def deserialise(s):
    l = json.loads(s, object_hook=as_petlib2)
    return tuplify(l)
    
# end of serialisation helper routines
############################################################################################

def readIssuerKeys():
    # read the key data from a file
    with open('/vagrant/Project/IssuerKeyFile.key', 'r') as f:
        s = f.read()
    (x, y) = deserialise(s)
    #global issuer_state
    state = BLcred.StateHolder()
    state.params = params
    state.x = x
    state.y = y  
    print "x = " + str(x)
    print "y = " + str(y)    
    return state

if __name__ != "__main__":    
    LT_issuer_state = readIssuerKeys()
    
if __name__ == "__main__":
    print("This is run standalone to create the issuer key file ...")
    LT_issuer_state, issuer_pub = BLcred.BL_issuer_keys(params)
    # write the private, public key to a file
    serialisation = serialise((LT_issuer_state.x,LT_issuer_state.y))
    print "x = " + str(LT_issuer_state.x)
    print "y = " + str(LT_issuer_state.y)
    with open('IssuerKeyFile.key', 'w') as f:
        f.write(serialisation)

#--------------------------------------------------------------------------------------------------------------------------------------------------


def getParams():
	#check if file exists
		#if yes, read and return values from it 

	#else, make it

	try:
		fo = open("params.json", "r")

		parsed_json = json.load(fo)
		print ("G: " + parsed_json['G'])
		print("q:" + parsed_json['q'])
		print("g:" + parsed_json['g'])
		print("h:" + parsed_json['h'])
		print("z:" + parsed_json['z'])
		#print("hs:" + parsed_json['hs'])

		fo.close()
	except (IOError, OSError) as e:
		fo = open("params.json", "w+")
		#write and return params

		G, q, g, h, z, hs = BLcred.BL_setup()

		print("G:" + str(G))
		print("q:" + str(q))
		print("g:" + str(g))
		print("h:" + str(h))
		print("z:" + str(z))
		#print("hs:" + str(hs))

		j = {"G": G,
			"q": q,
			"g": g,
			"h": h,
			"z": z,
			"hs":hs
		}

		json.dump(j, fo)

		fo.close()

#if __name__ == "__main__":
	#getParams()
#	print (BLcred.BL_setup())