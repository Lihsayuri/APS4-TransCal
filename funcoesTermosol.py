# -*- coding: utf-8 -*-
"""
A funcao 'plota' produz um gráfico da estrutura definida pela matriz de nos N 
e pela incidencia Inc.

Sugestao de uso:

from funcoesTermosol import plota
plota(N,Inc)
-------------------------------------------------------------------------------
A funcao 'importa' retorna o numero de nos [nn], a matriz dos nos [N], o numero
de membros [nm], a matriz de incidencia [Inc], o numero de cargas [nc], o vetor
carregamento [F], o numero de restricoes [nr] e o vetor de restricoes [R] 
contidos no arquivo de entrada.

Sugestao de uso:
    
from funcoesTermosol import importa
[nn,N,nm,Inc,nc,F,nr,R] = importa('entrada.xlsx')
-------------------------------------------------------------------------------
A funcao 'geraSaida' cria um arquivo nome.txt contendo as reacoes de apoio Ft, 
deslocamentos Ut, deformacoes Epsi, forcas Fi e tensoes Ti internas. 
As entradas devem ser vetores coluna.

Sugestao de uso:
    
from funcoesTermosol import geraSaida
geraSaida(nome,Ft,Ut,Epsi,Fi,Ti)
-------------------------------------------------------------------------------

"""
import math
from traceback import print_list




def plota(N,Inc):
    # Numero de membros
    nm = len(Inc[:,0])
    
    import matplotlib as mpl
    import matplotlib.pyplot as plt

#    plt.show()
    fig = plt.figure()
    # Passa por todos os membros
    for i in range(nm):
        
        # encontra no inicial [n1] e final [n2] 
        n1 = int(Inc[i,0])
        n2 = int(Inc[i,1])        

        plt.plot([N[0,n1-1],N[0,n2-1]],[N[1,n1-1],N[1,n2-1]],color='r',linewidth=3)


    plt.xlabel('x [m]')
    plt.ylabel('y [m]')
    plt.grid(True)
    plt.axis('equal')
    plt.show()
    
def importa(entradaNome):
    
    import numpy as np
    import xlrd
    
    arquivo = xlrd.open_workbook(entradaNome)
    
    ################################################## Ler os nos
    nos = arquivo.sheet_by_name('Nos')
    
    # Numero de nos
    nn = int(nos.cell(1,3).value)
                 
    # Matriz dos nós
    N = np.zeros((2,nn))
    
    for c in range(nn):
        N[0,c] = nos.cell(c+1,0).value
        N[1,c] = nos.cell(c+1,1).value
    
    ################################################## Ler a incidencia
    incid = arquivo.sheet_by_name('Incidencia')
    
    # Numero de membros
    nm = int(incid.cell(1,5).value)
                 
    # Matriz de incidencia
    Inc = np.zeros((nm,4))
    
    for c in range(nm):
        Inc[c,0] = int(incid.cell(c+1,0).value)
        Inc[c,1] = int(incid.cell(c+1,1).value)
        Inc[c,2] = incid.cell(c+1,2).value
        Inc[c,3] = incid.cell(c+1,3).value
    
    ################################################## Ler as cargas
    carg = arquivo.sheet_by_name('Carregamento')
    
    # Numero de cargas
    nc = int(carg.cell(1,4).value)
                 
    # Vetor carregamento
    F = np.zeros((nn*2,1))
    
    for c in range(nc):
        no = carg.cell(c+1,0).value
        xouy = carg.cell(c+1,1).value
        GDL = int(no*2-(2-xouy)) 
        F[GDL-1,0] = carg.cell(c+1,2).value
         
    ################################################## Ler restricoes
    restr = arquivo.sheet_by_name('Restricao')
    
    # Numero de restricoes
    nr = int(restr.cell(1,3).value)
                 
    # Vetor com os graus de liberdade restritos
    R = np.zeros((nr,1))
    
    for c in range(nr):
        no = restr.cell(c+1,0).value
        xouy = restr.cell(c+1,1).value
        GDL = no*2-(2-xouy) 
        R[c,0] = GDL-1


    return nn,N,nm,Inc,nc,F,nr,R

def geraSaida(nome,Ft,Ut,Epsi,Fi,Ti):
    nome = nome + '.txt'
    f = open("saida.txt","w+")
    f.write('Reacoes de apoio [N]\n')
    f.write(str(Ft))
    f.write('\n\nDeslocamentos [m]\n')
    f.write(str(Ut))
    f.write('\n\nDeformacoes []\n')
    f.write(str(Epsi))
    f.write('\n\nForcas internas [N]\n')
    f.write(str(Fi))
    f.write('\n\nTensoes internas [Pa]\n')
    f.write(str(Ti))
    f.close()
    


nn,N,nm,Inc,nc,F,nr,R = importa(entradaNome='entrada.xlsx')
# print(N)

def calculo_L_angulos(N, Inc):
    linhas, colunas = N.shape
    dict_nos = {}
    dict_l = {}
    for i in range(colunas):
        x = N[0][i]
        y = N[1][i]
        dict_nos[i+1] = [x, y]

    # print(dict_nos)
    linhas_inc, colunas_inc = Inc.shape

    # print(Inc)

    for j in range(linhas_inc):
        no1 = Inc[j][0]
        no2 = Inc[j][1]
        x1, y1 = dict_nos[no1]
        x2, y2 = dict_nos[no2]
        l = math.sqrt((x1-x2)**2+(y1-y2)**2)
        sen = (y2-y1)/l
        cos = (x2-x1)/l
        dict_l[j+1] = [l, sen, cos, Inc[j][2], Inc[j][3]]
    
    
    # print(dict_l)


    return(dict_l)


def calcula_Ke(dict_l):
    import numpy as np
    dict_Ke = {}
    dict_K_elemento = {}

    # print("Essas são as restrições :", R)
    # print(nr)

    for elm in dict_l.keys():
        E = dict_l[elm][3]
        A = dict_l[elm][4]
        s = dict_l[elm][1]
        c = dict_l[elm][2]
        L = dict_l[elm][0]

        dict_Ke[elm] =  [[c**2, c*s, -c**2, -c*s],
                        [c*s, s**2, -c*s, -s**2],
                        [-c**2, -c*s, c**2, c*s],
                        [-c*s, -s**2, c*s, s**2]]

        k = ((E*A)/L)
        dict_K_elemento[elm] = np.multiply(dict_Ke[elm], k)

    return dict_K_elemento

dict_L = calculo_L_angulos(N, Inc)
dict_cada_elemento = calcula_Ke(dict_L)
print("RESTRIÇÃO: ", R)


plota(N,Inc)

# def montaMatrizesRigidez(nm):



# nn = número de nós
# nm = número de elementos
# N = matriz dos nós
# nm = número dos membros
# nr = numero de restricoes 





