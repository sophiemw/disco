import datetime, base64, json
import BLcred
from petlib.bn import Bn
from petlib.ec import EcGroup, EcPt

from hashlib import sha256
from base64 import b64encode

params = BLcred.BL_setup()
(G, q, g, h, z, hs) = params

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
    s = json.dumps(t, separators=(',', ':'), cls=petlibEncoder)
    return s

    
def deserialise(s):
    l = json.loads(s, object_hook=as_petlib2)
    return tuplify(l)
    
# end of serialisation helper routines
############################################################################################

def create_issuer_state():
    state = BLcred.StateHolder()
    state.params = params
    state.x = x
    state.y = y 

    return state

############################################################################################

def readIssuerKeys():
    # read the key data from a file
    with open('IssuerKeyFile_public.key', 'r') as f:
        s = f.read()
    y = deserialise(s)

    try:
        with open('IssuerKeyFile_private.key', 'r') as f:
            s = f.read()
        x = deserialise(s)
    except Exception, e:
        x = None
        pass

    #global issuer_state
#    state = BLcred.StateHolder()
#    state.params = params
#    state.x = x
#    state.y = y  
#    print "x = " + str(x)
#    print "y = " + str(y)   

    return (x, y)

if __name__ != "__main__":    
    (x, y) = readIssuerKeys()
    
if __name__ == "__main__":
    print("This is run standalone to create the issuer key files ...")
    LT_issuer_state, issuer_pub = BLcred.BL_issuer_keys(params)
    # write the private, public key to files    

    # This should only be run once
    # Private key should only be in the bank folder - just run this file in the bank
    # and then copy the public files into the other folders
    serialisation = serialise(LT_issuer_state.x)
    print "x = " + str(LT_issuer_state.x)
    with open('IssuerKeyFile_private.key', 'w') as f:
        f.write(serialisation)

    serialisation = serialise(LT_issuer_state.y)
    print "y = " + str(LT_issuer_state.y)
    with open('IssuerKeyFile_public.key', 'w') as f:
        f.write(serialisation)

############################################################################################


def test_Hash(params):
    # There is a lot of Hashing going on - make it into a function rather than inline it each time...
    # Make the Hashing more general purpose by using the str() function for each class type. 
    # EcPT__str__() gives a different encoding than export() 
    # Hstr = list(map(EcPt.export, params))
    Hstr = list(str(e) for e in params)
    Hhex = b"|".join(map(b64encode, Hstr))
    return Bn.from_binary(sha256(Hhex).digest())

############################################################################################


def spending_1(im):
    (G, q, g, h, z, hs) = params

    # http://stackoverflow.com/questions/415511/how-to-get-current-time-in-python
    datetime2 = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
    print("datetime2 " + datetime2)

    desc = test_Hash([im, datetime2]) % q

    return desc


def spending_2(tau, gam, coin, desc):
    (G, q, g, h, z, hs) = params

    epsilonp = test_Hash([tau * z] + list(coin) + [desc]) % q

    mup = (tau - epsilonp * gam) % q

    msg_to_merchant_epmupcoin = (epsilonp, mup, coin)

    return msg_to_merchant_epmupcoin


def spending_3(msg_to_merchant_epmupcoin, desc):
    (epsilonp, mup, coin) = msg_to_merchant_epmupcoin
    (m, zet, zet1, zet2, om, omp, ro, ro1p, ro2p) = coin
    (G, q, g, h, z, hs) = params

    #assert zet != 1 

    assert epsilonp == (test_Hash([mup * z + epsilonp * zet] + list(coin) + [desc]) % q)

    lhs = (om + omp) % q
    rhs_h = [zet, zet1, 
            ro * g + om * y,
            ro1p * g + omp * zet1,
            ro2p * h + omp * zet2, ## problem
            mup * z + epsilonp * zet]

    Hstr = list(map(EcPt.export, rhs_h)) + [b'']
    Hhex = b"|".join(map(b64encode, Hstr))
    rhs = Bn.from_binary(sha256(Hhex).digest()) % q

    return (lhs == rhs)

############################################################################################
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

############################################################################################
def doublespendcalc(epsilonp, mup, epsilonp2, mup2, zet1):
    # Confirm that we can work out who the guilty party is...
    # We have (epsilonp, mup) for first validation, and (epsilonp2, mup2) for the second validation

#    print("epsilonp:    " + str(epsilonp))
#    print("epsilonp2:   " + str(epsilonp2))
#    print("mup:         " + str(mup))
#    print("mup2:        " + str(mup2))
#    print("zet1:        " + str(zet1))

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
#    print "z1calc  = " + str(serialise(z1calc))
    return z1calc

############################################################################################
# Table 8: Revealing the attribute
# add Attribute Reveal Protocol
# L1 - amount
# L2 - expiry date
    
def rev_attribute_1(Lj, gam, zet, zet1, rnd, R, att):
    (rnd, )= rnd
    L1, L2 = att 
    if Lj == "amount": 
        Lj = L1
        j = 1
    if Lj == "expirydate": 
        Lj = L2
        j = 2
    

    # Wallet side calculations
    rndp = q.random()
    Cp = (Lj * gam) * hs[j] + (rndp * gam) * g
    r, rp, r0, r1, r2 = [q.random() for _ in range(5)]
    rj = (r0, r1, r2)[j]
    rgam = q.random()

    zet1h = r0 * hs[0] + r1 * hs[1] + r2 * hs[2] + r * g
    Cph = rj * hs[j] + rp * g
    # recall zet from before
    zeth = rgam * z
    hjp = gam * hs[j]
    hjh = rgam * hs[j]
    cpdiv = (rndp * gam) * g
    cljh = rp * g
    c = test_Hash( [zet1, zet1h, Cp, Cph, "date/time", zet, zeth, hjp, hjh, cpdiv, cljh] )

    s0 = (r0 + c * R    * gam) % q
    s1 = (r1 + c * L1   * gam) % q
    s2 = (r2 + c * L2   * gam) % q
    s  = (r  + c * rnd  * gam) % q
    sp = (rp + c * rndp * gam) % q
    sgam = (rgam + c * gam) % q
    # wallet now reveals Lj, zet1, zet1h, Cp, Cph, s0..s2, s, sp, sgam, zet, zeth, hjp, hjh, cljh
    return (Lj, j, zet1, zet1h, Cp, Cph, s0, s1, s2, s, sp, sgam, zet, zeth, hjp, hjh, cljh)
  

def rev_attribute_2(values):
    Lj, j, zet1, zet1h, Cp, Cph, s0, s1, s2, s, sp, sgam, zet, zeth, hjp, hjh, cljh = values
    
    sj = (s0, s1, s2)[j]

    # Merchant/Bank side validations
    # merchant side is given all the input parameters to the hash, so no need to recalc that here - it's Fiat-Shamir
    
    cpdiv = Cp -(Lj * hjp)
    c = test_Hash( [zet1, zet1h, Cp, Cph, "date/time", zet, zeth, hjp, hjh, cpdiv, cljh] )

    lhs = zet1h + c * zet1
    rhs = s0 * hs[0] + s1 * hs[1] + s2 * hs[2] + s * g
    
    lhs1 = Cph + c * Cp
    rhs1 = sj * hs[j] + sp * g

    lhs2 = zeth + c * zet
    rhs2 = sgam * z

    lhs3 = hjh + c * hjp
    rhs3 = sgam * hs[j]

    lhs4 = cljh + c * cpdiv
    rhs4 = sp * g

    a = lhs  == rhs
    b = lhs1 == rhs1
    c = lhs2 == rhs2
    d = lhs3 == rhs3
    e =  lhs4 == rhs4

    return (a and b and c and d and e, Lj)


############################################################################################
# Proof of knowledge - pi
def pi_proof_wallet(C, R, L1, L2):
    # recall that user's C
    # C = R * hs[0] + L1 * hs[1] + L2 * hs[2]

    # wallet side
    Cp = R * hs[0]
    rnd = q.random()
    a = rnd * hs[0]
    c_wallet = test_Hash( [a, hs[0], Cp] )
    r = rnd + R * c_wallet

    # send over c_wallet, r, a, C, Cp, L1, L2
    pi_proof_values = c_wallet, r, a, C, Cp, L1, L2
    return pi_proof_values


def pi_proof_bank(pi_proof_values):
    c_wallet, r, a, C, Cp, L1, L2 = pi_proof_values

    # bank side
    c_bank = test_Hash( [a, hs[0], Cp] )
    assert c_wallet == c_bank

    lhs1 = r * hs[0]
    rhs1 = c_bank * Cp + a

    lhs2 = C
    rhs2 = Cp + L1 * hs[1] + L2 * hs[2]

    return (lhs1 == rhs1) and (lhs2 == rhs2)