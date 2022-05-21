from tkinter import *
import numpy as np
from math import *
import random
#1: Passage d'une carte net à une carte de pression

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

Image = Image.open( r"C:\Users\Jean-Baptiste\Pictures\Couleur_rogné.PNG" )
image_array = np.asarray( Image )    #asarray pour empecher la modification de l'image

# plt.imshow( image_array )
# plt.show()



# Creation image


hauteur = 100
largeur = 300
# mode RGB
canal = 3
new_array_RGB = np.zeros([hauteur, largeur, canal], dtype = np.uint8)


#Modification de l'image

# rouge : première tranche 0, 100
new_array_RGB[:,:100,:] = (255, 0, 0)
# vert : deuxième tranche 100, 200
new_array_RGB[:,100:200,:] = (0, 255, 0)
# bleu : Troisième tranche 200, 300
new_array_RGB[:,200:,:] = (0, 0, 255)



passage_couleur_température=np.array( [[[73,61,217],[73,93,223],[85,74,219],-14 ], [[80,128,232],[93,163,241],[91,136,233],-10 ], [[105,193,248],[116,213,251],[113,191,247],-6 ], [[153,230,255],[179,238,249],[138,225,245],-2 ], [[51,242,150],[51,233,217],[97,240,177],2 ], [[51,211,109],[64,194,149],[45,171,125], 6], [[84,149,125],[51,142,84],[33,119,64], 10],  [[99,180,86],[148,217,89],[124,189,69],14 ], [[196,255,92],[224,249,180],[169,225,72],18 ],  [[255,248,51],[249,229,60],[225,218,33],22 ],  [[253,213,61],[253,189,55],[223,185,42],26 ], [[249,161,51],[255,133,51],[255,140,64],30 ], [[253,114,51],[255,52,255],[254,66,64],34 ],[[245,72,51],[245,70,129],[246,82,136],38 ], [[245,69,255],[221,63,163],[221,80,183],42 ], [[195,58,121],[170,53,77],[199,71,129],46 ]],dtype=object)

matrice_couleur=np.array([[[245,69,255,255],[99,180,86, 255],[195,58,121, 255]],[[253,213,61,255],[169,225,72,255] ,[255,248,51, 255] ]])
#Matrice 42,14,46// 26,18,22


def verification_1(liste):
    for i in range(len(liste)//2):
        if liste[2*i]==0:
            return False
    return True

def liste_pixels_possibles(i,j,carte):
    """Renvoie une liste de 16*3*2 éléments. Il s'agit des pixels possibles ou non de passage_couleur_température pouvant désigner la température de carte[i][j]. Ils sont accollés à un 0 ou un 1 selon que ce pixel soit possible ou non"""
    liste=[]
    for k in range(16):  #la liste passage_couleur_température contient 16 éléments
        for e in range(3):
            b=0      #0=True et 1= False
            for f in range(3):
                if abs(passage_couleur_température[k][e][f] - carte[i][j][f])>=40:   # Lien entre les pixels et les couleurs
                    b=1
            liste.append(b)   #Au final, elle est de de taille 16*3*2. Les 0 donnent les triplets cohérent en température
            liste.append(e)
    return liste


température=np.zeros(6)
température=température.reshape(2,3)


def liste_pixels_possibles_2(i,j,carte,matrice_température):
    """Idem mais en vérifiant une certaine continuité entre la case et la case précédente sur la ligne"""
    liste=[]
    for k in range(16):  #la liste passage_couleur_température contient 16 éléments
        for e in range(3):
            b=0
            for f in range(3):
                if abs(passage_couleur_température[k][e][f] - carte[i][j][f])>=40:   # Lien entre les pixels et les couleurs
                    b=1
            if abs(matrice_température[i][j-1] - passage_couleur_température[k][3])>=12: #Condition de continuité de la température
                b=1
           # print(k)
           # print(b)
            liste.append(b)   #Finalement, elle est de de taille 16. Les True donnent les lieux cohérent en température
            liste.append(e)
    return liste



def indice_RGB(carte,liste,i,j,e,n):
    """Donne l'indice dans la liste correspondant à la température associé au pixel étudié"""
    indice=0
    for k in range(16):
        valeur=1000     #Ecart entre le pixel étudié est celui de référence
        if liste[6*k]==0 or liste[6*k+2]==0 or liste[6*k+4]==0:
            rep=True    #La température associée à ces 3 éléments est possible
            if liste[k*6]==0:
                e=liste[6*k+1]    #e est le triplet RGB possiblement caractéristique du pixel étudié
                valeur1=0
                for f in range(3):
                    valeur1+=abs(passage_couleur_température[k][e][f] - carte[i][j][f])
                valeur=min(valeur,valeur1)
            elif liste[6*k+2]==0 :
                e=liste[6*k+2]
                valeur2=0
                for f in range(3):
                    valeur2+=abs(passage_couleur_température[k][e][f] - carte[i][j][f])
                valeur=min(valeur,valeur2)    #On conserve la difference la plus faible
            elif liste[6*k+4]==0:
                e=liste[6*k+5]
                valeur3=0
                for f in range(3):
                    valeur3+=abs(passage_couleur_température[k][e][f] - carte[i][j][f])
                valeur=min(valeur,valeur3)
        else:
            valeur=1000      #Cas d'une température non caractéristique du pixel
        if valeur<n:
            n=valeur
            indice=k
    return indice

liste_pix=liste_pixels_possibles_2(1,2,matrice_couleur,température)


def passage_carte_couleur_carte_température(carte):
    n,m=len(carte),len(carte[0])
    mat_temp=np.zeros(n*m)
    mat_temp=mat_temp.reshape(n,m)
    for i in range(n):
        liste_couleur=liste_pixels_possibles(i,0,carte)
        indice=indice_RGB(carte,liste_couleur,i,0,e,1000)    #indice de la liste numpy associé à la température à renvoyer. 1000 car les différences entre les pixels étudiés et les pixels de références sont bien inférieur à 1000
        mat_temp[i][0]=passage_couleur_température[indice][3]

        for j in range(1,m):            #On traite le cas général
            liste_couleur=liste_pixels_possibles_2(i,j,carte,mat_temp)

            if verification_1(liste_couleur):
                mat_temp[i][j]=mat_temp[i][j-1]    #On s'assure de la continuité avec la cae précédente si le pixel est illisible
            else:
                rep=False
                indice=indice_RGB(carte,liste_couleur,i,j,e,1000)
                if rep:
                    mat_temp[i][j]=mat_temp[i][j-1]
                else:
                    mat_temp[i][j]=passage_couleur_température[indice][3]  #On extraie la température associée  à l'indice pour lequel cette différence est la plus faible
    return mat_temp


#verification: la commande passage_carte_couleur_carte_température(matrice_couleur) renvoie:
#array([[42., 42., 46.],
 #      [26., 18., 22.]])


#matrice=passage_carte_couleur_carte_température(image_array)


# Travail sur le passage de carte de température au sol à carte de pression





constante=3.9*10**-3  #Constante  calculé dans la démo de la fonction passage_temperature_sol_pression(M,Tsol) dans l'open office
P0=100000
altitude=9000   #La température ne varie pas entre 9 et 20 km (à peu près)
g=9.81
R=8.31

def passage_température_sol_pression(M,Tsol):  #M en kg/mol, Tsol la température au sol
    return P0*((Tsol-constante*altitude)/Tsol)**(M*g/(constante*R)) #Demo dans l'open office

#passage_temperature_sol_pression(32*10**-3,300)
# 29961.576428490323



def passage_carte_température_pression(M,matrice_température):  #M en kg/mol car g en m3/(kg.s)
    n,m=len(matrice_température),len(matrice_température[0])
    matrice_pression=np.zeros(n*m)
    matrice_pression=matrice_pression.reshape(n,m)
    for i in range(n):
        for j in range(m):
            matrice_pression[i][j]=passage_température_sol_pression(M,matrice_température[i][j])
    return matrice_pression



#passage_carte_température_pression(32*10**-3, matrice_type)
# avec matrice_type: array([[301, 302, 303, 304, 305],
       # [306, 307, 308, 309, 310],
       # [311, 312, 313, 314, 315],
       # [316, 317, 318, 319, 320],
       # [321, 322, 323, 324, 325],
       # [326, 327, 328, 329, 330],
       # [331, 332, 333, 334, 335],
       # [336, 337, 338, 339, 340],
       # [341, 342, 343, 344, 345],
       # [346, 347, 348, 349, 350]])

# On obtient: array([[30089.57559298, 30217.21237519, 30344.48718533, 30471.40045348,
       #  30597.95262898],
       # [30724.14417994, 30849.97559274, 30975.44737149, 31100.5600376 ,
       #  31225.31412926],
       # [31349.71020099, 31473.74882317, 31597.43058161, 31720.75607711,
       #  31843.72592502],
       # [31966.34075485, 32088.60120981, 32210.50794648, 32332.06163434,
       #  32453.26295547],
       # [32574.1126041 , 32694.6112863 , 32814.7597196 , 32934.55863263,
       #  33054.00876479],
       # [33173.11086593, 33291.865696  , 33410.27402473, 33528.33663132,
       #  33646.05430416],
       # [33763.42784049, 33880.45804613, 33997.14573521, 34113.49172984,
       #  34229.4968599 ],
       # [34345.16196272, 34460.48788284, 34575.47547176, 34690.12558769,
       #  34804.4390953 ],
       # [34918.41686546, 35032.05977506, 35145.36870674, 35258.34454866,
       #  35370.98819432],
       # [35483.30054232, 35595.28249618, 35706.93496407, 35818.25885871,
       #  35929.25509709]])





#2 Travail passage carte de pression à carte d'accélération

#On travail avec des matrices n*m

n=10
m=5
matrice_type=np.arange(1,n*m+1) + 300
matrice_type=matrice_type.reshape(n,m)  #Matrice type pour faire des exemples simples



Rt=6371000
theta=23.0+26/60*100      #angle equateur/tropique (23°26')
def distance_equateur_tropique():
    """donne la distance equateur//tropique"""
    return sqrt(2*(Rt**2)*(1+cos(theta)))



hauteur_carte=12560000
largeur_carte=40075000



def taille_case(carte_pression):
    """Prend la carte de pression et renvoie la taille réel des cases en m (hauteur de la case, largeur de la case)"""
    n,m=len(carte_pression),len(carte_pression[0])
    return hauteur_carte/n,largeur_carte/m



def passage_carte_pression_carte_acceleration_selon_x(masse_volumique,carte_pression):
    """Donne une matrice dont les coordonnées sont les accélérations selon x en ce point de la matrice"""
    n,m=len(carte_pression),len(carte_pression[0])   #Matrice Mn,m(R)
    matrice_1_x=[]
    dx,dy=taille_case(carte_pression)
    for i in range(n):    #travaillons d'abord les coordonnées selon ex
        liste=[]
        for j in range(m-1):
           liste.append((carte_pression[i][j] - carte_pression[i][j+1])/(dx*masse_volumique))    #On ajoute l'acceleration selon ex
        liste.append((carte_pression[i][m-1] - carte_pression[i][0])/(dx*masse_volumique))  #On ajoute l'acceleration selon ex au bord
        matrice_1_x.append(liste)
    matrice_final=[]  #On cherche maintenant à donner les accélérations moyennes entre 2 bords
    for i in range(n):
        liste=[]
        liste.append((matrice_1_x[i][0] + matrice_1_x[i][m-1])/2)   #On travail sur le bord
        for j in range(m-1):
            liste.append((matrice_1_x[i][j] + matrice_1_x[i][j+1])/2)  #(ax1-ax2)/2
        matrice_final.append(liste)
    return matrice_final



acc_x=passage_carte_pression_carte_acceleration_selon_x(32,matrice_type)


def passage_carte_pression_carte_acceleration_selon_y(masse_volumique,carte_pression):
    n,m=len(carte_pression),len(carte_pression[0])   #Matrice Mn,m(R)
    matrice_1_y=[]
    dx,dy=taille_case(carte_pression)
    for i in range(n-1):
        liste=[]
        for j in range(m):    #les bords du haut et du bas ne se rejoignent pas. Cela est traité ailleurs
            liste.append((carte_pression[i][j] - carte_pression[i+1][j])/(dy*masse_volumique))
        matrice_1_y.append(liste)
    matrice_final=[]
    for j in range(m):
        liste=[]
        liste.append(matrice_1_y[0][j])   #On considère que l'accélération sur la 1 ere case est l'accélération au bord inférieur
        for i in range(n-2):
            liste.append((matrice_1_y[i][j] + matrice_1_y[i+1][j])/2)
        liste.append(matrice_1_y[n-2][j])
        matrice_final.append(liste)
    return matrice_final


acc_y=passage_carte_pression_carte_acceleration_selon_x(32,matrice_type)


#3: Passage d'une situation initiale (quantité de matière initiale, sa position, la vitesse initiale en tout point) à une table de l'instant initiale (carte vitesse à t0 ET carte des quantités de matières à t0) (def init)




def init_vitesse_x(position,n,m):
    """Entrée: une liste position dont les éléments sont du type [i,j,quantité de matière, vitesses selon x, vitesses selon y] avec i et j les indices des positions (dans le cas de cases vides, pas besoin de le préciser dans la liste position), n et m les dimensions de la matrice finale et renvoie une matrice avec les quantités de matières initiallement, une matrice avec les vitesses initiales selon x et les vitesses initiales selon y"""
    matrice_vit_x_init=np.zeros(n*m)
    matrice_vit_x_init=matrice_vit_x_init.reshape(n,m)
    for k in range(len(position)):
        matrice_vit_x_init[position[k][0] - 1][position[k][1] - 1]=position[k][3] # -1 s'explique par la différence d'indicage entre une matrice classique et une matrice python
    return matrice_vit_x_init



def init_vitesse_y(position,n,m):
    """Entrée: une liste position dont les éléments sont du type [i,j,quantité de matière, vitesses selon x, vitesses selon y] avec i et j les indices des positions (dans le cas de cases vides, pas besoin de le préciser dans la liste position), n et m les dimensions de la matrice finale et renvoie une matrice avec les quantités de matières initiallement, une matrice avec les vitesses initiales selon x et les vitesses initiales selon y"""
    matrice_vit_y_init=np.zeros(n*m)
    matrice_vit_y_init=matrice_vit_y_init.reshape(n,m)
    for k in range(len(position)):
        matrice_vit_y_init[position[k][0] - 1][position[k][1] - 1]=position[k][4]
    return matrice_vit_y_init



def init_matiere(position,n,m):
    """Entrée: une liste position dont les éléments sont du type [i,j,quantité de matière, vitesses selon x, vitesses selon y] avec i et j les indices des positions (dans le cas de cases vides, pas besoin de le préciser dans la liste position), n et m les dimensions de la matrice finale et renvoie une matrice avec les quantités de matières initiallement, une matrice avec les vitesses initiales selon x et les vitesses initiales selon y"""
    matrice_mat_init=np.zeros(n*m)
    matrice_mat_init=matrice_mat_init.reshape(n,m)
    for k in range(len(position)):
        matrice_mat_init[position[k][0] - 1][position[k][1] - 1]=position[k][2]  # -1 s'explique par la différence d'indicage entre une matrice classique et une matrice python
    return matrice_mat_init


matrice_vitesse_x_avant=init_vitesse_x([[2,1,2.244,9876,123]],10,5)
matrice_vitesse_y_avant=init_vitesse_y([[2,1,2.244,9876,123]],10,5)
matrice_matiere_avant=init_matiere([[2,1,2.244,9876,123]],10,5)

#4 Passage d'une carte des vitesses à l'instant t, le temps total du traitement, le nombre de sous intevalles de temps et de la carte des accélérations à la carte des vitesses à l'instant t + dt (def update_vitesse)


def evolution_vitesse_x(acceleration_x,vitesse_x_t,t_total,k,n,m):
    dt=t_total/k
    vitesse_x_dt=np.zeros(n*m)
    vitesse_x_dt=vitesse_x_dt.reshape(n,m)
    for i in range(n):
        for j in range(m):
            vitesse_x_dt[i][j]=vitesse_x_t[i][j] + acceleration_x[i][j]*dt
    return vitesse_x_dt



def evolution_vitesse_y(acceleration_y,vitesse_y_t,t_total,k,n,m):
    dt=t_total/k
    vitesse_y_dt=np.zeros(n*m)
    vitesse_y_dt=vitesse_y_dt.reshape(n,m)
    for i in range(n):
        for j in range(m):
            vitesse_y_dt[i][j]=vitesse_y_t[i][j] + acceleration_y[i][j]*dt
    return vitesse_y_dt




matrice_vitesse_x_apres=evolution_vitesse_x(acc_x,matrice_vitesse_x_avant,32000,50,10,5)
matrice_vitesse_y_apres=evolution_vitesse_y(acc_y,matrice_vitesse_y_avant,32000,50,10,5)




#5 Travail sur les pôles

t_total=1000000
k=10000


def intervalle_temps(t_total,k):
    return t_total/k



def deplacement_aléatoire(i_sortie,j_sortie,carte_pression):
    """Entrée: les indices de la case de sortie de la quantité de matière
       Sortie: la distance entre le point d'entréeet le bord de la carte et les indices de la case d'entrée"""
    distance=random.randint(0,largeur_carte)
    hauteur_case,largeur_case=taille_case(carte_pression)
    distance_totale=largeur_case * i_sortie + distance    #distance par rapport au bord
    if distance_totale>largeur_carte:
        distance_totale=distance_totale - largeur_carte
        i_entrée=distance_totale//largeur_case
    else:
       i_entrée=distance_totale//largeur_case
    if distance_totale<i_sortie*largeur_case:
        distance= -distance       #On prend en compte le fait que la molecule peut se deplacer vers la gauche
    return distance, i_entrée, j_sortie


def temps_aléatoire(v_init_x,distance):
    """Entrée: la distance entre le point de sortie est d'entrée et la vitesse de sortie selon x
       Sortie: le temps aléatoire pour lequel la particule ressort du pôle"""
    temps_min=abs(distance)/abs(v_init_x)
    temps_min += random.randint(0,int(temps_min))   #On met un int car ne marche pas avec un float
    return temps_min

i=4
j=2
dist,i_entrée_elementaire, j_sortie_elementaire=deplacement_aléatoire(i,j,matrice_type)
t_sortie_elementaire=temps_aléatoire(matrice_vitesse_x_apres[i][j],dist)

#dist=6069401, i_entrée_elementaire=4.0, j_sortie_elementaire=2
#t_sortie_elementaire=1091319609267.9999


def arrondie_temps(t,dt):
    """Entrée: un temps, dt
       Sortie: le nombre de dt nécessaire pour atteindre t"""
    return int(dt*(t//dt))


t_sortie_elementaire_final=arrondie_temps(t_sortie_elementaire,t_total/k)

#1091319609200


def passage_position_élémentaire(v_init_x,v_init_y,t_initial,i_sortie,j_sortie,n,liste,carte_pression):
    """Entrée: la vitesse de sortie du groupe de particules, le temps où l'on fait ce passage, les indices de sortie du bloc de particule, la quantité de particule élémentaire, la liste à l'instant t des éléments dans les pôles qui doivent être renvoyé. Cette liste est trié selon les temps. [i,j,t,v_x,v_y,n]
    Sortie: la liste à l'instant t + dt triée"""
    taille_liste=len(liste)
    distance,i_entrée,j_entrée=deplacement_aléatoire(i_sortie,j_sortie,carte_pression)
    element=[i_entrée, j_entrée, arrondie_temps(temps_aléatoire(v_init_x,distance), t_total/k),v_init_x, -v_init_y,n]    #Information sur l'element de matière considéré
    e=0
    for i in range(taille_liste):
        if element[2]>liste[i][2]:
            e+=1           #indice d'injection des informations sur la quantité elementaire
        else:
            break
    liste.insert(e,element)
    return liste


pas_elementaire=passage_position_élémentaire(2,4,100,2,4,10,[[1,2,10,15,12,30]],matrice_type)
# [[1, 2, 10, 15, 12, 30], [1.0, 4, 31919600, 2, -4, 10]]

#6 passage d'une carte des vitesses à l'instant t, d'une carte des quantités de matières à l'instant t et de la taille des cellules à une carte des vitesses à t + dt et une carte des quantités de matières à t + dt (def update_matière)

#7 Création de la fonction totale : temps de la mesure finale, table initial, carte accélération -> Table final

#8 def extraction : table final -> Image avec les quantités de matières

