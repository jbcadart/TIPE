from tkinter import *
import numpy as np
from math import *
#1: Passage d'une carte net à une carte de pression

#Travail sur tkinter
#mainapp=tkinter.Tk() #construction de la fenêtre tkinter
#mainapp.title("Programme TIPE")
#mainapp.minsize(640,480) #Taille minimale de l'image par défaut
#mainapp.maxsize(1280,720) #Idem mais l'inverse
#mainapp.resizable(width=False, height=True) #Autorise ou non de s'étendre en hauteur ou en largeur

#mainapp.geometry("800x600") #800 pixels x 600 pixels

#label_welcome=tkinter.Label(mainapp, text="coucou")

#print(label_welcome.cget("text")) #Ecrit dans le shell l'élément appelé, ici le texte de label_welcome

#label_welcome.config(text="Nouveau message") #permet de modifier le paramètre d'un widget

#entry_name=tkinter.Entry(mainapp,width=45) #Créer une barre de taille 45 dans lequel on peut écrire

#label_welcome.pack()
#mainapp.mainloop() #boucle infini jusqu'à un certain moment
#Resultat= Un widget (une fenêtre en gros)





#Travail sur l'image du monde

# fen=Tk()
# fen.attributes("-fullscreen",1)
#
# fond=Canvas(fen,width=1920, height=1080, highlightthickness=1,bg='red')
# fond.place(x=0,y=0)
# fichier=PhotoImage(r"C:\Users\Jean-Baptiste\Desktop\Prépa MPSI\Carte.png")
# #image=fond.create_image(150,100,image=fichier,anchor="nw")
# fichier
# plt.chow()
#
#
#
#
#
#
#
# fen.mainloop()




# Travail sur le passage de carte de température au sol à carte de pression

constante=3.9*10**-3  #Constante  calculé dans la démo de la fonction passage_temperature_sol_pression(M,Tsol) dans l'open office
P0=100000
altitude=9000   #La température ne varie pas entre 9 et 20 km (à peu près)

def passage_temperature_sol_pression(M,Tsol):  #M en kg/mol, Tsol la température au sol
    return P0*((Tsol-constante*altitude)/Tsol)**(M*9.81/(constante*8.31)) #Demo dans l'open office

#2 Travail passage carte de pression à carte d'accélération

#On travail avec des matrices n*m

n=10
m=5
matrice_type=np.arange(1,n*m+1)
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





#3: Passage d'une situation initiale (quantité de matière initiale, sa position, la vitesse initiale en tout point) à une table de l'instant initiale (carte vitesse à t0 ET carte des quantités de matières à t0) (def init)


def init(position,n,m):
    """Entrée: une liste position dont les éléments sont du type [i,j,quantité de matière, vitesses selon x, vitesses selon y] avec i et j les indices des positions (dans le cas de cases vides, pas besoin de le préciser dans la liste position), n et m les dimensions de la matrice finale et renvoie une matrice avec les quantités de matières initiallement, une matrice avec les vitesses initiales selon x et les vitesses initiales selon y"""
    matrice_mat_init=np.zeros(n*m)
    matrice_mat_init=matrice_mat_init.reshape(n,m)
    matrice_vit_x_init=np.zeros(n*m)
    matrice_vit_x_init=matrice_vit_x_init.reshape(n,m)
    matrice_vit_y_init=np.zeros(n*m)
    matrice_vit_y_init=matrice_vit_y_init.reshape(n,m)
    for k in range(len(position)):
        matrice_mat_init[position[k][0] - 1][position[k][1] - 1]=position[k][2]  # -1 s'explique par la différence d'indicage entre une matrice classique et une matrice python
        matrice_vit_x_init[position[k][0] - 1][position[k][1] - 1]=position[k][3]
        matrice_vit_y_init[position[k][0] - 1][position[k][1] - 1]=position[k][4]
    return matrice_mat_init,matrice_vit_x_init,matrice_vit_y_init

#4 Passage d'une carte des vitesses à l'instant t et de la carte des accélérations à la carte des vitesses à l'instant t + dt (def update_vitesse)

#5 Travail sur les pôles

#6 passage d'une carte des vitesses à l'instant t, d'une carte des quantités de matières à l'instant t et de la taille des cellules à une carte des vitesses à t + dt et une carte des quantités de matières à t + dt (def update_matière)

#7 Création de la fonction totale : temps de la mesure finale, table initial, carte accélération -> Table final

#8 def extraction : table final -> Image avec les quantités de matières

