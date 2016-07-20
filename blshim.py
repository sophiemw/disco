import datetime, base64, json
import BLcred
from petlib.bn import Bn
from petlib.ec import EcGroup, EcPt

from hashlib import sha256
from base64 import b64encode

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


#--------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------------------------------------------------------

def test_Hash(params):
    # e-coin: There is a lot of Hashing going on - make it into a function rather than inline it each time...
    # e-coin: Make the Hashing more general purpose by using the str() function for each class type. 
    # e-coin: EcPT__str__() gives a different encoding than export() 
    # e-coin: Hstr = list(map(EcPt.export, params))
    Hstr = list(str(e) for e in params)
    Hhex = b"|".join(map(b64encode, Hstr))
    return Bn.from_binary(sha256(Hhex).digest())


def spending_1(im):
    (G, q, g, h, z, hs) = params
#    im = "merchantaccount details"

    # http://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
    datetime2 = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    print("datetime2 " + datetime2)

    # https://docs.python.org/2/library/hashlib.html
    #desc = sha256((im, datetime)).hexdigest()

    # H = [im, datetime]
#    Hstr = [im, datetime]
#    Hhex = b"|".join(map(b64encode, Hstr))
#    desc = Bn.from_binary(sha256(Hhex).digest()) % q

    desc = test_Hash([im, datetime2]) % q

    return desc

def spending_2(tau, gam, coin, desc):
#    tau = user_state.tau
    (G, q, g, h, z, hs) = params
#    gam = user_state.gam

#    H = [tau * z, coin, desc]
#    Hstr = 

    epsilonp = test_Hash([tau * z] + list(coin) + [desc]) % q

    mup = (tau - epsilonp * gam) % q
   # print(mup.__class__.__name__)

    msg_to_merchant_epmupcoin = (epsilonp, mup, coin)

    return msg_to_merchant_epmupcoin

def spending_3(msg_to_merchant_epmupcoin, desc):

    (epsilonp, mup, coin) = msg_to_merchant_epmupcoin
    (m, zet, zet1, zet2, om, omp, ro, ro1p, ro2p) = coin
    (G, q, g, h, z, hs) = params

    #TOOD
    #assert zet != 1 

    #a = (mup * z + epsilonp * zet, coin, desc)
    #assert epsilonp == sha256(a).hexdigest()
    assert epsilonp == (test_Hash([mup * z + epsilonp * zet] + list(coin) + [desc]) % q)

    lhs = (om + omp) % q
    rhs_h = [zet, zet1, 
            ro * g + om * LT_issuer_state.y,
            ro1p * g + omp * zet1,
            ro2p * h + omp * zet2, ## problem
            mup * z + epsilonp * zet]

    #rhs = test_Hash(rhs_h) % q

    Hstr = list(map(EcPt.export, rhs_h)) + [b'']
    Hhex = b"|".join(map(b64encode, Hstr))
    rhs = Bn.from_binary(sha256(Hhex).digest()) % q

    return (lhs == rhs)


# see http://www.johannes-bauer.com/compsci/ecc/
def eea(i, j):
    assert(isinstance(i, Bn))
    assert(isinstance(j, Bn))
    (s, t, u, v) = (Bn(1), Bn(0), Bn(0), Bn(1))
    while j != 0:
        #(q, r) = (i // j, i % j)
        (q, r) = divmod(i, j)
        (unew, vnew) = (s, t)
        s = u - (q * s)
        t = v - (q * t)
        (i, j) = (j, r)
        (u, v) = (unew, vnew)
    (d, m, n) = (i, u, v)
    return (d, m, n)
    
# inverse of i % q
def inv(i, q):
    (d, m, n) = eea(q, i)
    return m


def doublespendcalc(epsilonp, mup, epsilonp2, mup2, zet1):
    # Confirm that we can work out who the guilty party is...
    # We have (epsilonp, mup) for first validation, and (epsilonp2, mup2) for the second validation

    print("epsilonp:    " + str(epsilonp))
    print("epsilonp2:   " + str(epsilonp2))
    print("mup:         " + str(mup))
    print("mup2:        " + str(mup2))
    print("zet1:        " + str(zet1))


    mupd = (mup2 - mup) % q
    epsilonpd = (epsilonp - epsilonp2) % q
    
    #gamma = (mup2 - mup) / (epsilonp - epsilonp2) # truncation on division- fail
    gamma = mupd * inv(epsilonpd, q) % q
    invGamma = epsilonpd * inv(mupd, q) % q
    reallyOne = gamma * invGamma % q
#    print "gamma =     " + str(gamma)
#    print "invGamma =  " + str(invGamma)
#    print "reallyOne = " + str(reallyOne)
    
    z1calc = invGamma * zet1
#    print "z1      = " + str(z1)
    print "z1calc  = " + str(serialise(z1calc))
    return z1calc