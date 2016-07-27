import time
import random
import math

people = [('Seymour','BOS')
        ,('Franny','DAL')
        ,('Zooey','CAK')
        ,('Walt','MIA')
        ,('Buddy','ORD')
        ,('Les','OMA')]
destination='LGA'
flights={}
for line in open('data/schedule.txt'):
    origin,dest,depart,arrive,price=line.strip().split(',')
    flights.setdefault((origin,dest),[])
    flights[(origin,dest)].append((depart,arrive,int(price)))
def getminutes(t):
    x = time.strptime(t,"%H:%M")
    return x[3]*60 + x[4]

def printschedule(r):
    for d in range(len(r)/2):
        name=people[d][0]
        origin=people[d][1]
        out=flights[(origin,destination)][r[2*d]]
        ret=flights[(destination,origin)][r[2*d+1]]
        print  '%10s%10s %5s-%5s $%3s %5s-%5s $%3s' % \
        (name,origin,out[0],out[1],out[2],ret[0],ret[1],ret[2] )
def schedulecost(sol):
    totalprice=0
    latestarrival=0
    earliestdep=24*60

    for d in range(len(sol)/2):
        origin = people[d][1]
        outbound=flights[(origin,destination)][int(sol[2*d])]
        returnf=flights[(destination,origin)][int(sol[2*d+1])]

        totalprice += outbound[2]
        totalprice += returnf[2]
        if latestarrival<getminutes(outbound[1]):latestarrival=getminutes(outbound[1])
        if earliestdep > getminutes(returnf[0]):earliestdep = getminutes(returnf[0])
    totalwait=0
    for d in range(len(sol)/2):
        origin = people[d][1]
        outbound=flights[(origin,destination)][int(sol[2*d])]
        returnf=flights[(destination,origin)][int(sol[2*d+1])]
        totalwait += latestarrival - getminutes(outbound[1])
        totalwait += getminutes(returnf[0])-earliestdep 
        
    if latestarrival>earliestdep:totalprice+=50
    return totalprice+totalwait
def randomoptimize(domain,costf):
    best=999999999
    bestr=None
    for i in range(1000):
        r=[random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))]
        cost = costf(r)
        if cost < best:
            best=cost
            bestr=r
    return r        
def hillclimb(domain,costf):
    sol = [random.randint(domain[i][0],domain[i][1])
            for i in range(len(domain)) ]
    loop=0
    while 1:
        neighbors=[]
        for i in range(len(domain)):
            if sol[i] > domain[i][0]:
                neighbors.append( sol[0:i] + [sol[i]-1] + sol[i+1:]  )
            if sol[i] < domain[i][1]:
                neighbors.append(sol[0:i]+ [sol[i]+1] + sol[i+1:])
        
        current = costf(sol)
        best = current
        for j in range(len(neighbors)):
            cost = costf(neighbors[j])
            loop+=1         
            if cost < best:
                best = cost
                sol = neighbors[j] 
        if best == current:
            print "hill climb run:%d" % loop
            break
    return sol
def annealingoptimize(domain,costf,T=10000.0,cool=0.95,step=1):
    sol=[ random.randint(domain[i][0],domain[i][1]) 
        for i in range(len(domain))] 
    loop = 0
    while T > 0.1:
        i=random.randint(0,len(domain)-1)
        dir=random.randint(-step,step)
        vecb = sol[:]
        vecb[i]=+dir
        if vecb[i] < domain[i][0]:
            vecb[i]=domain[i][0]
        if vecb[i] > domain[i][1]:
            vecb[i]=domain[i][1]
        
        ea=costf(sol)
        eb=costf(vecb)
        if eb < ea or random.random() < pow(math.e,-(eb-ea)/float(T)):
            sol = vecb
        T = T*cool
        loop +=1            
    print "annealing loop:%d" % (loop)
    return sol

def geneticoptimize(domain,costf,popsize=50,step=1,mutprob=0.2
    ,elite=0.2,maxiter=100):
    def mutate(vec):
        i=random.randint(0,len(domain)-1)
        if random.random()<0.5 and vec[i]>domain[i][0]:
            return vec[0:i] + [vec[i]-step] + vec[i+1:]
        elif vec[i] < domain[i][1]:
            return vec[0:i] + [ vec[i]+1] + vec[i+1:]
        return vec[:]
    def crossover(r1,r2):
        i=random.randint(0,len(domain))
        return r1[:i] + r2[i:]        
    pop=[]
    for i in range(popsize):
        pop.append([ random.randint(domain[i][0],domain[i][1]) for i in range(len(domain))])
    topelite=int(elite*popsize)
    for i in range(maxiter):
        scores=[ (costf(v),v) for v in pop] 
        scores.sort()
        ranked=[v for s,v in scores]
        print "geneitc iter",scores[0][0]    
        pop = ranked[:topelite]
        while len(pop) < popsize:
            if random.random()<mutprob:
                pop.append(mutate(ranked[random.randint(0,topelite-1)]))
            else:
                c1,c2=(ranked[random.randint(0,topelite-1)] for i in range(2))
                pop.append(crossover(c1,c2))    
    return scores[0][1] 
                            
if __name__ == '__main__':
    s = [0] * 12
    #printschedule(s)
    domain=[(0,1)] * len(people)*2
    s = randomoptimize(domain,schedulecost)
    print s
    printschedule(s)
    print schedulecost(s)

    ret = hillclimb(domain,schedulecost)
    print ret
    printschedule(ret)
    print schedulecost(ret)         
    
    ret = annealingoptimize(domain,schedulecost)
    print ret
    printschedule(ret)
    print schedulecost(ret)         
    
    ret = geneticoptimize(domain,schedulecost)
    print ret
    printschedule(ret)
    print schedulecost(ret)         
