print("alakazoum...")

from tkinter import *
import numpy as np
from math import *
import random
#1: Passage d'une carte net à une carte de pression

import numpy as np
import matplotlib.pyplot as plt
from PIL import Image

from types import SimpleNamespace
import tkinter as tk
from tkinter import ttk

import json
from datetime import datetime
import time



class Vect2(tuple):
    def __add__(self, a):
        # TODO: check lengths are compatable.
        return Vect2(x + y for x, y in zip(self, a))
    def __sub__(self, a):
        # TODO: check lengths are compatable.
        return Vect2(x - y for x, y in zip(self, a))
    def __mul__(self, c):
        return Vect2(x * c for x in self)
    def __rmul__(self, c):
        return Vect2(c * x for x in self)
VectNul = Vect2( (0, 0) )



def dist(a, b):
    return sqrt((a[0]-b[0])**2 + (a[1]-b[1])**2)

def getColor(t):
    t = max(0, min(1, t))
    return rgb_hack( ((1-t)*color0[0]+t*colorMax[0], (1-t)*color0[1]+t*colorMax[1], (1-t)*color0[2]+t*colorMax[2]) )

def rgb_hack(rgb):
    return "#%02x%02x%02x" % rgb



#================================================================

#ALERT !!
#Les coord de mes Cell sont TOUJOURS celles de son CENTRE (et pas celles de son coin bas gauche)
#ALERT !!

#On travaille en radians et en mètres
#le point de coordonées 0,0 se trouve en long = 0, lat = -latitudeMaxPoles
#la case d'indice 0, 0 se trouve en long = 0, lat = -latitudeMaxPoles


#constantes physiques
rayonTerre = 6.371e6
masse_vol_soufre = 32*10**-3    #je n'e ai actuellement aucune idée
timeNOW = 0

#constantes relatives à la carte
#suseptibles d'être changées
largeurMondeCell  = 20 #nombre de Cells en largeur  (en Y)
longueurMondeCell = 50 #nombre de Cells en longueur (en X)

#on se place au level 80
#donc
a_lnsp =19620.042969
b_lnsp = 0.068448



latitudeMaxPoles = radians(45)                   #Au dessus de cet angle, on est dans les pôles
#donc
largeurMonde = 2*rayonTerre*sin(latitudeMaxPoles)                       #taille (en mètre) (et en Y) du monde
longueurMonde = 2*pi*rayonTerre                                         #taille (en mètre) (et en X) du monde
#donc
largeurCell = largeurMonde/largeurMondeCell   # (en mètre) la taille (en Y) d'une cell
longueurCell = longueurMonde/longueurMondeCell # (en mètre) de même
hauteurCell  = 10   # (en mètre) complétement arbitraire, ne sert que pour l'homogénéité des formules
#donc
A0 = largeurCell * longueurCell  #Aire d'une Cell
V0 = A0 * hauteurCell           #Volume d'une Cell

tkLongueurCell = 20 #(en pixel, uniquement pour le dessin)
tkLargeurCell = 20 #(en pixel, uniquement pour le dessin)
tkOffsetX = 100
tkOffsetY = 100

#intervalle temps
t_total=1000000
k=10000

dt = t_total/k

#constante calcul pression
constante=3.9*10**(-3)  #Constante  calculé dans la démo de la fonction passage_temperature_sol_pression(M,Tsol) dans l'open office
P0=100000
altitude=9000   #La température ne varie pas entre 9 et 20 km (à peu près)
g=9.81
R=8.31

def taille_case(carte_pression):
    """Prend la carte de pression et renvoie la taille réel des cases en m (hauteur de la case, largeur de la case)"""
    n,m=len(carte_pression),len(carte_pression[0])
    return largeurCell,longueurCell

#Couleurs tkinter
#couleur quand il n'y a pas de soufre
color0 = (220, 220, 190)

#couleur quand il y a satSoufre ou plus
colorMax = (255, 70, 35)
satSoufre = 20 #au pif pour l'instant


#----------------------
print("Constantes + import ok !")


Image = Image.open( r"C:\Users\Jean-Baptiste\Desktop\Prépa MPSI\TIPE\Capture.21.05.2022.PNG" )
image_array = np.asarray( Image )    #asarray pour empecher la modification de l'image

# plt.imshow( image_array )
# plt.show()
#1 Passage température sur carte en couleur à matrice de température


passage_couleur_température=np.array( [[[73,61,217],[73,93,223],[85,74,219],-14 ], [[80,128,232],[93,163,241],[91,136,233],-10 ], [[105,193,248],[116,213,251],[113,191,247],-6 ], [[153,230,255],[179,238,249],[138,225,245],-2 ], [[51,242,150],[51,233,217],[97,240,177],2 ], [[51,211,109],[64,194,149],[45,171,125], 6], [[84,149,125],[51,142,84],[33,119,64], 10],  [[99,180,86],[148,217,89],[124,189,69],14 ], [[196,255,92],[224,249,180],[169,225,72],18 ],  [[255,248,51],[249,229,60],[225,218,33],22 ],  [[253,213,61],[253,189,55],[223,185,42],26 ], [[249,161,51],[255,133,51],[255,140,64],30 ], [[253,114,51],[255,52,255],[254,66,64],34 ],[[245,72,51],[245,70,129],[246,82,136],38 ], [[245,69,255],[221,63,163],[221,80,183],42 ], [[195,58,121],[170,53,77],[199,71,129],46 ]],dtype=object)

matrice_couleur=np.array([[[245,69,255,255],[99,180,86, 255],[195,58,121, 255]],[[253,213,61,255],[169,225,72,255] ,[255,248,51, 255] ]])
#Matrice 42,14,46// 26,18,22



def liste_pixels_possibles(i,j,carte):
    """Renvoie une liste de 16*3*2 éléments. Il s'agit des pixels possibles ou non de passage_couleur_température pouvant désigner la température de carte[i][j]. Ils sont accollés à un 0 ou un 1 selon que ce pixel soit possible ou non"""
    liste=[]
    for k in range(16):  #la liste passage_couleur_température contient 16 éléments
        for e in range(3):
            b=0      #0=True et 1= False
            for f in range(3):
                if abs(passage_couleur_température[k][e][f] - carte[i][j][f])>=60:   # Lien entre les pixels et les couleurs
                    b=1
            liste.append(b)   #Au final, elle est de de taille 16*3*2. Les 0 donnent les triplets cohérent en température
            liste.append(e)
    return liste



#température=np.zeros(6)
#température=température.reshape(2,3)



def liste_pixels_possibles_2(i,j,carte,matrice_température):
    """Idem mais en vérifiant une certaine continuité entre la case et la case précédente sur la ligne"""
    liste=[]
    for k in range(16):  #la liste passage_couleur_température contient 16 éléments
        for e in range(3):
            b=0
            for f in range(3):
                if abs(passage_couleur_température[k][e][f] - carte[i][j][f])>=60:   # Lien entre les pixels et les couleurs
                    b=1
            if abs(matrice_température[i][j-1] - passage_couleur_température[k][3])>=16: #Condition de continuité de la température
                b=1
            liste.append(b)   #Finalement, elle est de de taille 16. Les True donnent les lieux cohérent en température
            liste.append(e)
    return liste


#liste_pixels_possibles_2(1,2,matrice_couleur,température)
#[1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2, 1, 0, 1, 1, 1, 2]


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




def verification_1(liste):
    for i in range(len(liste)//2):
        if liste[2*i]==0:
            return False
    return True




def passage_carte_couleur_carte_température(carte):
    n,m=len(carte),len(carte[0])
    mat_temp=np.zeros(n*m)
    mat_temp=mat_temp.reshape(n,m)
    for i in range(n):
        liste_couleur=liste_pixels_possibles(i,0,carte)
        indice=indice_RGB(carte,liste_couleur,i,0,e,1000)    #indice de la liste numpy associé à la température à renvoyer. 1000 car les différences entre les pixels étudiés et les pixels de références sont bien inférieur à 1000
        mat_temp[i][0]=passage_couleur_température[indice][3]
        if i!=0:
            if abs(mat_temp[i-1][0]- mat_temp[i][0])>=12:
                mat_temp[i][0]=mat_temp[i-1][0]

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
            if i!=0:
                if abs(mat_temp[i-1][j]- mat_temp[i][j])>=12:
                    mat_temp[i][j]=mat_temp[i-1][j]
    return mat_temp

print("Image Pixel ok !")

#matrice_temp_couleur=passage_carte_couleur_carte_température(matrice_couleur)

#verification: la commande passage_carte_couleur_carte_température(matrice_couleur) renvoie:
#array([[42., 42., 46.],
 #      [26., 18., 22.]])


#matrice=passage_carte_couleur_carte_température(image_array)

# with open('output.txt','w') as f1:
#     json.dump(matrice.tolist(),f1)


#matrice[120]

print("matrice temp ok !")

#définition de Carte et Cell, soit le "meat and potatoes" de la simulation


#Travail Théo

class Cell:

    def __init__(self, estUnPole, masse, i, j, taille = Vect2((longueurCell, largeurCell))):

        if estUnPole:
            #vraies variables
            self.ls =[]
            
            #Variables qui ne servent à rien
            #juste à éviter des ErrorNotFound quand on importe
            self.m = masse                                          #masse de SOUFRE dans la Cell

            self.a = Vect2((0, 0))                                  #acc de l'AIR
            self.v = Vect2((0, 0))                                  #vitesse de l'AIR

            self.t = taille                                         #Taille (largeur longueur) de la cell
            self.V = self.t[0]*self.t[1]*hauteurCell                #volume de la cell

            self.ij = (i, j)
            self.coord = Vect2(((i+0.5)*longueurCell, (j+0.5)*largeurCell))

            self.pression = 0                                       #valeur par défaut

            #==========================
            #variables seulement pour l'importation de la base de données
            self.val = 0
            self.nbData = 0
            
            

        else:
            self.m = masse                                          #masse de SOUFRE dans la Cell
            self.a = Vect2((0, 0))                                  #acc de l'AIR
            self.v = Vect2((0, 0))                                  #vitesse de l'AIR

            self.t = taille                                         #Taille (largeur longueur) de la cell
            self.V = self.t[0]*self.t[1]*hauteurCell                #volume de la cell

            self.ij = (i, j)
            self.coord = Vect2(((i+0.5)*longueurCell, (j+0.5)*largeurCell))

            self.pression = 0                                       #valeur par défaut

            #==========================
            #variables seulement pour l'importation de la base de données
            self.val = 0
            self.nbData = 0


class Carte: #l'objet que doit gérer Jb

   
#3: Passage d'une situation initiale (quantité de matière initiale, sa position, la vitesse initiale en tout point) à une table de l'instant initiale


    def __init__(self): #Par exemple

        self.cells = []

        for i in range(longueurMondeCell):
            self.cells.append([])
            for j in range(largeurMondeCell):
                self.cells[i].append(Cell(False, 0, i, j, Vect2((longueurCell, largeurCell)))) #on initialise les cell à une qté nulle de soufre
                #self.cells[i][j] =

        self.poleNord = Cell(True, 0, -1, -1)
        self.poleSud = Cell(True, 0, -1, -1)

    def cellFromCoord(self, coord):
        #Je mets en entrée des distances (en Mètres)

        x = coord[0]
        y = coord[1]

        if abs(y) > largeurMonde:
            if y < 0:
                return self.poleSud
            else:
                return self.poleNord
        else:
            indX = int(x//longueurCell) % longueurMondeCell
            indY = int(y//largeurCell)

            return self.cells[indX][indY]

    def cellFromLatLongRad(self, latitude, longitude):
        #je mets en entrée des coordonnées du monde réel ***(latitude longitude)***. L'entrée peut être négative, pointer sur les pôles, être à la jonction de 2 cells
        #j'ai en sortie la cell dans laquelle je tombe (donc soit une cell, soit les pôles)
        #si je suis sur une ligne, c'est le droite haut qui gagne

        #Mes lat,long sont des RADIANS, et sont algébriques

        if abs(latitude) >= latitudeMaxPoles:
            if latitude > 0:
                return self.poleNord
            else:
                return self.poleSud

        else:
            largeurCalc = rayonTerre*sin(latitude)  #on a une distance
            indY = int((largeurCalc + largeurMonde/2)//largeurCell)

            longueurCalc = longitude*rayonTerre      #on a une distance
            indX = int(longueurCalc//longueurCell) % longueurMondeCell

            return self.cells[indX][indY]

    def cellFromLatLongDeg(self, latitude, longitude):
        return self.cellFromLatLongRad(radians(latitude), radians(longitude))


    def cellsFromCellAndCoord(self, cell):
        #c'est le fameux truc que j'ai demandé à Cointault : quand j'additione les coords de la case à son vecteur vitesse, quelles cases je touche et dans quelles proportions ?
        #en sortie j'ai une liste tuples (cell, float) avec les cells que je touche et quelle proportion (avec le float)

        coord = cell.coord

        #je sais quelles cases mes extrémités touchent
        coordCoinDH = coord + Vect2( ( cell.t[0]/2,  cell.t[1]/2) ) + cell.v #coin droite haut
        coordCoinDB = coord + Vect2( ( cell.t[0]/2, -cell.t[1]/2) ) + cell.v
        coordCoinGB = coord + Vect2( (-cell.t[0]/2, -cell.t[1]/2) ) + cell.v
        coordCoinGH = coord + Vect2( (-cell.t[0]/2,  cell.t[1]/2) ) + cell.v

        cellCoinDH = self.cellFromCoord(coordCoinDH)
        cellCoinDB = self.cellFromCoord(coordCoinDB)
        cellCoinGB = self.cellFromCoord(coordCoinGB)
        cellCoinGH = self.cellFromCoord(coordCoinGH)

        xinter = (coordCoinDH[0] // longueurCell) #+ coordCoinDH[0] % longueurCell
        yinter = (coordCoinDH[1] // largeurCell) #+ coordCoinDH[1] % largeurCell
        vectInter = Vect2((xinter, yinter))

        aireDH = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        aireDB = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        aireGB = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        aireGH = (dist(cellCoinDH, vectInter)/sqrt(2))**2
        #normalement, on a aireDH + ... + aireGH = largeurCell*longueurCell (=A0)

        rep = []
        rep.append( (cellCoinDH, aireDH/A0) )
        rep.append( (cellCoinDB, aireDB/A0) )
        rep.append( (cellCoinGB, aireGB/A0) )
        rep.append( (cellCoinGH, aireGH/A0) )

        #donc return [ [cell, float]; [...] ]
        return rep

    #4 Passage de la carte des vitesses de l'instant t à l'instant t+dt
    def accToVitesse(self, cell):
        cell.v += cell.a * dt

    def updateCells(self, matriceAccAir):

        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):

                cell = self.cells[i][j]

                cell.a = Vect2((0, 0))
                cell.a = matriceAccAir[i][j]

                self.accToVitesse(cell)


                destinations = self.cellsFromCellAndCoord(cell)
                #on enlève le soufre dans la case originelle
                m0 = cell.m
                cell.m = 0
                #pour enventuellement le remettre si il ne s'est pas trop déplacé
                for e in destinations:
                    if e[0].estUnPole:
                        #à remplir
                        e[0].ls += [transition_position_élémentaire(cell.v, timeNOW, i, j, m0*e[1])]
                        #[i,j,t_auquel_il_doit_sortir,v_x,v_y,m]
                            
                    else:
                        e[0].val += m0*e[1]    #on le met dans .val temporairement car on ne peut pas le mettre directement dans .m
        
        #UpdatePoles
        for e in self.poleNord.ls:                                          #[i,j,t_auquel_il_doit_sortir,v_x,v_y,m]
            if e[2] > timeNOW:
                self.cells[e[0]][e[1]].val += e[5]                          #self.cells[i][j].val += m
                

        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                cell = self.cells[i][j]

                cell.m = cell.val
                
    def matrice_Pression(self): 
        #nous donne la matrice des pressions (de la taille longueurMondeCell*largeurMondeCell)
        #C'est juste un recopiage de valeurs
        matRep = []
        for i in range(longueurMondeCell):
            matRep.append([])
            for j in range(largeurMondeCell):
                matRep[i].append(self.cells[i][j].pression)
         
        return matRep
        
    def passageTempPression(self):
        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                c0 = self.cells[i][j]
                c0.pression = P0*((c0.val + 273.15-constante*altitude)/(c0.val+273.15))**(masse_vol_soufre*g/(constante*R))

    def draw(self):

        for i in range(longueurMondeCell):
            for j in range(largeurMondeCell):
                newColor = getColor(self.cells[i][j].m/satSoufre)
                canvas.create_rectangle( i*tkLongueurCell + tkOffsetX, (largeurMondeCell-j-1)*tkLargeurCell + tkOffsetY,
                                         (i+1)*tkLongueurCell+ tkOffsetX,  (largeurMondeCell-j)*tkLargeurCell + tkOffsetY,
                                         fill=newColor, dash=(1))


                
#fonctions de controle, les mainLoop :

def Update(carte0, carte_pression):
    
    matriceAccAir = passage_carte_pression_carte_acceleration_selon_x_et_y( carte_pression )
    
    carte0.updateCells(matriceAccAir)

def Draw():
    carte0.draw()
    tk.update_idletasks()
    tk.update()

def animate (carte0):
    
    Update(carte0, carte0.matrice_Pression())
    
    timeNOW += dt
    print(timeNOW)
   
    time.sleep(0.01)

print("Cells + Carte ok !")  
    
    
    
    
#Passage température globale à température moyennée


def importBigArray(carte0, ba):
    #[temp]

    n = len(ba)
    m = len(ba[0])

    #on calcule la taille (en "mètres") d'un pixel
    longueurPixelX = longueurMonde/m
    largeurPixelY = largeurMonde/n

    for i in range(n):
        for j in range(m):
            #!!!!!! Le point 0, 0 est en haut à gauche alors que moi il est en bas à gauche
            cell0 = carte0.cellFromCoord(Vect2( ( (j)*longueurPixelX, (n-i)*largeurPixelY) ))
            cell0.val += ba[i][j]
            cell0.nbData += 1

    for i in range(longueurMondeCell):
        for j in range(largeurMondeCell):
            if (carte0.cells[i][j].nbData != 0):
                carte0.cells[i][j].val = carte0.cells[i][j].val/carte0.cells[i][j].nbData

    carte0.passageTempPression()

    
    
    
#Passage température pression

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
    # for j in range(m):
    #     liste=[]
    #     liste.append(matrice_1_y[0][j])   #On considère que l'accélération sur la 1 ere case est l'accélération au bord inférieur
    #     for i in range(n-2):
    #         liste.append((matrice_1_y[i][j] + matrice_1_y[i+1][j])/2)
    #     liste.append(matrice_1_y[n-2][j])
    #     matrice_final.append(liste)
    #
    liste=[]
    for j in range(m):
        liste.append(matrice_1_y[0][j])
    matrice_final.append(liste)
    for i in range(n-2):
        liste=[]
        for j in range(m):
            liste.append((matrice_1_y[i][j] + matrice_1_y[i+1][j])/2)
       # liste.append(matrice_1_y[n-2][j])
        matrice_final.append(liste)
    liste=[]
    for j in range(m):
        liste.append(matrice_1_y[n-2][j])
    matrice_final.append(liste)
    return matrice_final

def passage_carte_pression_carte_acceleration_selon_x_et_y (carte_pression):
    matX = passage_carte_pression_carte_acceleration_selon_x(masse_vol_soufre, carte_pression)
    matY = passage_carte_pression_carte_acceleration_selon_y(masse_vol_soufre, carte_pression)

    (n, m) = len(carte_pression), len(carte_pression[0])
    mat_fin = []
    for i in range(n):
        mat_fin.append([])
        for j in range(m):
            mat_fin[i].append( (matX[i][j], matY[i][j]) )
            
    return mat_fin
                                                               
                                                                                                                              

#5 Travail sur les pôles


def deplacement_aléatoire(i_sortie,j_sortie,carte_pression):
    """Entrée: les indices de la case de sortie de la quantité de matière
       Sortie: la distance entre le point d'entrée et le bord de la carte et les indices de la case d'entrée"""
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

#i=4
#j=2
#dist,i_entrée_elementaire, j_sortie_elementaire=deplacement_aléatoire(i,j,matrice_type)
#t_sortie_elementaire=temps_aléatoire(matrice_vitesse_x_apres[i][j],dist)

#dist=6069401, i_entrée_elementaire=4.0, j_sortie_elementaire=2
#t_sortie_elementaire=1091319609267.9999

#1091319609200

def transition_position_élémentaire(v_init,t_initial,i_sortie,j_sortie,m):
    """Entrée: la vitesse de sortie du groupe de particules, le temps où l'on fait ce passage, les indices de sortie du bloc de particule, la quantité de particule élémentaire,
    [i,j,t,v_x,v_y,m]
    Sortie: la liste à l'instant t + dt triée"""
    
    distance,i_entrée,j_entrée=deplacement_aléatoire(i_sortie,j_sortie)
    element=[i_entrée, j_entrée,t_initial + temps_aléatoire(v_init[0],distance),v_init[0], -v_init[1],m]    #Information sur l'element de matière considéré
    
    return element


# pas_elementaire=transition_position_élémentaire(2,4,100,2,4,10,[[1,2,10,15,12,30]],matrice_type)
# [[1, 2, 10, 15, 12, 30], [1.0, 4, 31919600, 2, -4, 10]]

print("import + logique poles ok !")   
                                                                 
#===========================================================================================================================================================================                                                          
#====================================================================================================================================================================================================
#========================================================================================================================================================================

#on exécute le code ici

#========================================================================================================================================================================
#========================================================================================================================================================================
print("on commence !!!!!!!!!!!")

carte_init=Carte()
importBigArray(carte_init,matrice)
carte_init.cells[15][15].m += 50

for i in range(longueurMondeCell):
    ls = []
    for j in range(largeurMondeCell):
        ls.append(carte_init.cells[i][j].val)
    #print(ls)
                                                                 
while True:
    animate(carte_init)                                                                
                                                                 
                                                                 
