import pandas as pd
import math
import json

data = pd.read_csv('data.csv')
context_day=pd.read_csv('context_day.csv')
context_place=pd.read_csv('context_place.csv')
#print(data)

count_row = data.shape[0]  # gives number of row count
count_col = data.shape[1]  # gives number of col count

print(count_col)
print(data[" Movie "+str(count_col-1)][0])
CountMovies=count_col-1
CountUsers=count_row
k = 4
UserId=29
#UserId=35
#Часть 1
def FindMark(MovieInd,UserInd):
    AvgMarkU=AvgUserMark(UserInd)
    numerator=0
    denominator=0
    FourSim=FindSim(UserInd)[:k]#берем только 4 самых похожих
   # print(FourSim)
    for i in range(0,k):
        numerator+=FourSim[i][1]* (data[" Movie "+str(MovieInd)][FourSim[i][0]]-AvgUserMark(FourSim[i][0]))
        denominator+=math.fabs(FourSim[i][1])
    mark=AvgMarkU+numerator/denominator
    return mark

def FindSim(UserInd):
    m = 0
    numerator=0
    SumU=0
    SumV=0
    SimDict={}
    for userV in range (0,count_row):
        if (UserInd!=userV):
            for i in range(1, count_col):
                if (data[" Movie " + str(i)][UserInd] != -1 and data[" Movie " + str(i)][userV] != -1):
                    m += 1
                    numerator+=data[" Movie " + str(i)][UserInd] * data[" Movie " + str(i)][userV]
                    #print( data[" Movie " + str(i)][UserInd] * data[" Movie " + str(i)][UserInd])
                    SumU =SumU+ data[" Movie " + str(i)][UserInd] * data[" Movie " + str(i)][UserInd]
                    SumV =SumV+ data[" Movie " + str(i)][userV] * data[" Movie " + str(i)][userV]
            res=numerator/(math.sqrt(SumU)*math.sqrt(SumV))
            #print(data[UserInd:UserInd+1].values[0][1:])
            #print(data[userV:userV + 1].values[0][1:])
            #print(numerator)
            #print(SumU)
            #print(SumV)
            SimDict[userV]=res
            numerator = 0
            SumU = 0
            SumV = 0
    # Сортируем так, чтобы самые похожие были сверху
    list_d = list(SimDict.items())
    #print(list_d)
    list_d.sort(key=lambda i: i[1],reverse=True)
    #print(list_d)
    return list_d


def AvgUserMark(UserInd):
    count=0
    res=0
    for i in range(1, count_col):
        mark=data[" Movie "+str(i)][UserInd]
        if mark!=-1:
            res += mark
            count += 1


    if(count!=0):
        return res/count
    return 0 #Что возвращать, если у пользователя везде будет -1?

#Здесь берется именно номер пользователя [1..N], а не его индекс
def GiveRes(UserNum):
    UserIndex=UserNum-1
    if UserIndex<0 and UserIndex>CountUsers-1:
        return
    dict = {}
    for i in range(1, count_col):
        if data[" Movie "+str(i)][UserIndex]==-1:
            mark = FindMark(i,UserIndex)
            dict[" Movie " + str(i)]=round(mark,3)
    return dict


#Часть 2

#Словарь пользователей и их лучший фильм, который они посмотрели в выходные
def FindUsersBestMovies(TargetUser):
    UserInd=TargetUser-1
    if UserInd < 0 and UserInd > CountUsers - 1:
        return
    dictUserBestMovies= {}
    dictAllUsers_BestMovie={}
    for userV in range(0, count_row):
        if (UserInd != userV):
            for i in range(1, count_col):
                if (data[" Movie " + str(i)][userV] != -1 and
                        (context_day[" Movie " + str(i)][userV]==' Sun' or context_day[" Movie " + str(i)][userV]==' Sat')
                        and context_place[" Movie " + str(i)][userV]==' h'
                        and data[" Movie " + str(i)][userV]>=AvgUserMark(userV)):
                    dictUserBestMovies[" Movie " + str(i)]=data[" Movie " + str(i)][userV]
            if len(dictUserBestMovies) > 1:
                list_d = list(dictUserBestMovies.items())
                list_d.sort(key=lambda i: i[1], reverse=True)
                #print(userV)
                #print(list_d)
                dictAllUsers_BestMovie[userV] = list_d[0][0]
                list_d.clear()
                dictUserBestMovies.clear()
    return dictAllUsers_BestMovie

def FindFilm(Sim,UsersBestMovies):
    for i in range(len(Sim)):
        for j in range(len(UsersBestMovies)):
            if Sim[i][0]==UsersBestMovies[j][0]:
                return UsersBestMovies[j][1]

def Mark(TargetUser,film):
    UserInd = TargetUser - 1
    if UserInd < 0 and UserInd > CountUsers - 1:
        return
    if (data[film][UserInd]!=-1):
        #print( type(data[film][UserInd]))
        return int(data[film][UserInd])
    else:
        dict=GiveRes(TargetUser)
        return dict[film]

#Вызов первой части задания
print("User "+str(UserId))
dict1 = GiveRes(UserId)

print(dict1)

#Вызов второй части задания
Sim=FindSim(UserId-1)
UsersBestMovies=list(FindUsersBestMovies(UserId).items())
#print(Sim)
#print(UsersBestMovies)

film=FindFilm(Sim,UsersBestMovies)
#print(film)
dict2={ film: Mark(UserId,film)}
print(dict2)
dictForJson={"User":UserId, "1":dict1,"2":dict2}
print(dictForJson)


with open('Var29.json', 'w') as json_file:
  json.dump(dictForJson, json_file)


#app_json = json.dumps(dictForJson)
#print(app_json)