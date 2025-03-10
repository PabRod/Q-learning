#this code is the workbench for q-learning
#it consists on a lifting particle that must reach a certain height
#it is only subjected to gravity
#Force applied to the particle might be fixed +F, -F or 0

import numpy as np
import math
import random
import matplotlib.pyplot as plt

m=1 #1kg mass
g=9.80 #gravity
dt=0.05 #simulation time
Final_height=100 #1m
Final_vel=0


#STATES are discretized 0-1-2-3...100..-101-102-110cm and speed is discretized in
n_pos=111
STATES=np.linspace(0,110,n_pos)

#SPEEDS are discretized -10,-9,-8...0,1,2,3...,50cm/s.
n_speeds=61
SPEEDS=np.linspace(-10,50,n_speeds)

#ROWS=    States (121*61=7381 rows)
#COLUMNS= Actions (9.9 , 9.7) two actions
Rows=n_pos*n_speeds
Columns=2

#initialize variables
x=np.linspace(1,2000,2000)
z_pos_goal=np.zeros(2000)
z_vel_goal=np.zeros(2000)
z_acel_goal=np.zeros(2000)
velocidad_final=np.zeros(2000)#ya veré como declaro esto
z_sequence=np.zeros(2000)#ya veré cómo declaro esto

#Initialize Q matrix
Q=np.ones((Rows,Columns))
goalState=101*n_speeds+11 #this is the index of the state where height=100cm and vel=0cm/s


alpha=0.5
gamma=0.5
epsilon=0.08
Actions=([9.9, 9.7])
goalCounter=0
logro=0

for episode in range(1,200000):
    # random initial state
    z_pos=np.zeros(2000)
    z_vel=np.zeros(2000)
    z_accel=np.zeros(2000)
    # must do this to delete previous values
    
    counter=0
    state=11 #let's choose the initial state always height 0, speed 0cm/s

    rand_action=np.random.permutation(Columns)
    action=rand_action[1] #current action

    print("episode",episode) #check

    z_accel_old=0
    z_vel_old=0
    z_pos_old=0 #initial conditions of the particle

    #must specify the initial speed and position for the state
    COCIENTE=(state // n_speeds) #operador // para cociente
    RESTO=(state % n_speeds) #operador % para restos
    #esto lo hago para saber en qué posición de la matriz Q estoy
    z_pos_old=COCIENTE
    z_vel_old=SPEEDS[RESTO+1]


    while (state!= goalState or state!= (goalState+n_speeds) or state!= (goalState-n_speeds) or state!= (goalState+1) or state!= (goalState+n_speeds+1) or state!= (goalState-n_speeds+1)):          # loop until find goal state and goal action

        ## Find the maximum value of each row
        if np.random.uniform() < epsilon:
            rand_action=np.random.permutation(Columns)
            action=rand_action[1] #current action
            F=Actions[action]
        # if not select max action in Qtable (act greedy)
        else:
            QMax=max(Q[state]) 
            max_indices=np.where(Q[state]==QMax)[0] # Identify all indexes where Q equals max
            n_hits=len(max_indices) # Number of hits
            max_index=int(max_indices[random.randint(0, n_hits-1)]) # If many hits, choose randomly
            F=Actions[max_index]
            
                
        #apply dynamic model to check the new state during 0.5seconds
        N=1
        
        for i in range(counter*N,1+N+counter*N):

            ## Choose sometimes the Force randomly
            if np.random.uniform() < epsilon:
                rand_action=np.random.permutation(Columns)
                action=rand_action[1] #current action
                F=Actions[action]
            # if not select max action in Qtable (act greedy)
            else:
                QMax=max(Q[state]) 
                max_indices=np.where(Q[state]==QMax)[0] # Identify all indexes where Q equals max
                n_hits=len(max_indices) # Number of hits
                max_index=int(max_indices[random.randint(0, n_hits-1)]) # If many hits, choose randomly
                F=Actions[max_index]
            
            
            z_accel[i]=(-g + F/m)*100 #apply the dynamic model to the particle [cm/s2]

            z_vel[i]=z_vel_old + (z_accel[i]+z_accel_old)/2*dt
            z_pos[i]=z_pos_old + (z_vel[i]+z_vel_old)/2*dt
            z_accel_old=z_accel[i]
            z_vel_old=z_vel[i]
            z_pos_old=z_pos[i]

            counter=counter+1
            #print("counter:",counter)

            if i>300:
                rand_state=np.random.permutation(Rows)
                state=rand_state[1]
                state=11
                counter=0
                break #


    #if negative height or velocity values, reward it very negatively.
    #If too big values, too
        if (min(z_pos)<0 or min(z_vel)<-10 or max(z_vel)>50 or max(z_pos)>109):
            Q[state,max_index]=-1 #penalty
            state=11
            break

        else:    #if positive values, do the loop

            rounded_pos=round(z_pos[i])  #round the height with no decimals %no funciona con términos negativos
            rounded_vel=round(z_vel[i])  #round the vel with no decimals %no funciona con términos negativos

        #find the new state after the dynamic model
            
             ## Find the maximum value of each row
            QMax=max(Q[state]) 
            max_indices=np.where(Q[state]==QMax)[0] # Identify all indexes where Q equals max
            n_hits=len(max_indices) # Number of hits
            max_index=int(max_indices[random.randint(0, n_hits-1)]) # If many hits, choose randomly
            

            index_1=np.where(STATES==rounded_pos)
            index_2=np.where(SPEEDS==rounded_vel)
            index_1=int(index_1[0])
            index_2=int(index_2[0])

            state_new=n_speeds*index_1 + index_2  #new state in Q matrix

            QMax=max(Q[state_new])  #selects the highest value of the row
          

        #REWARD
            A1=math.exp(-abs(rounded_pos-Final_height)/(0.1*110))
            A2=math.exp(-abs(rounded_vel-Final_vel)/(0.1*14))
            Reward=A1*A2*1000000  #takes into account pos and vel

            #Q VALUE update
            Q[state,max_index]=Q[state,max_index] + alpha*(Reward + gamma*(QMax - Q[state,max_index]))  #update Q value
            state=state_new  #select the new state
            

        #checking
            if (rounded_pos==100 or rounded_pos==99 or rounded_pos==101):
                logro=logro+1
                

                if (rounded_vel==0):
                    goalCounter=goalCounter+1
                    print("exito",goalCounter)
                    #z_pos_goal[goalCounter]=z_pos
                    #z_vel_goal[goalCounter]=z_vel
                    #z_acel_goal[goalCounter]=z_accel


    #this matrix is stored for the estimation of transition probabilities
    #matrix (value iteration algorithm)
        #z_sequence[episode+1]=z_pos


