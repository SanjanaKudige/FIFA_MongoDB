import pymongo
import pymysql
from pymongo import ReadPreference
from pymongo import MongoClient

#Connecting to mySql
sqldb = pymysql.connect(host='localhost', port=3306, user='sanjanakudige', passwd='********', db='mysql')
cursor = sqldb.cursor()

#Establish connection to Mongo
client = MongoClient('mongodb://localhost:27017/') #localhost and default port
mongodb = client.db2
teamscores_collection = mongodb.team_scores
playerdata_collection = mongodb.player_data

teamscoresquery="select Team, MatchDate, SCity, SName, Team1_Score, Team2_Score from fifa.teams JOIN fifa.game on (fifa.teams.TeamID = fifa.game.TeamID1 or fifa.teams.TeamID = fifa.game.TeamID2) JOIN fifa.stadiums on fifa.game.SID = fifa.stadiums.SID ORDER BY MatchDate;"
cursor.execute(teamscoresquery)
result = cursor.fetchall()
jsonobj =[]
for i in range(0,len(result)-1,2) :
    jsondoc = {"team" : result[i][0]}
    jsondoc["matchScore"] = [{"MatchDate" : result[i][1], "City" : result[i][2], "Stadium" : result[i][3], "Team1" : result[i][0], "Team1_Score" : result[i][4], "Team2" : result[i+1][0], "Team2_Score" : result[i][5]}]
    jsonobj.append(jsondoc)

print(jsonobj)
teamscores_collection.insert(jsonobj)

teamdict = {}
teamsdata = "select distinct(team), TeamID from fifa.teams, fifa.game where fifa.teams.TeamID = fifa.game.TeamID1 or fifa.teams.TeamID = fifa.game.TeamID2;"
cursor.execute(teamsdata)
teamNames = cursor.fetchall()
for team in teamNames:
    teamdict[team[1]] = team[0]
    
playerquery= "SELECT fifa.players.`FIFA Popular Name`, Team, TeamID1, TeamID2, fifa.game.GameID, fifa.players.PlayerID, `Position`, MatchDate, SCity, SName, Time FROM fifa.players JOIN fifa.starting_lineups on (fifa.players.PlayerID = fifa.starting_lineups.PlayerID and fifa.players.TeamID=fifa.starting_lineups.TeamID) JOIN  fifa.game on (fifa.starting_lineups.GameID = fifa.game.GameID and (fifa.starting_lineups.TeamID = fifa.game.TeamID1 or fifa.starting_lineups.TeamID = fifa.game.TeamID2))JOIN fifa.teams on fifa.teams.TeamID = fifa.starting_lineups.TeamID join fifa.stadiums on (fifa.starting_lineups.GameID =fifa.game.GameID and fifa.game.sid = fifa.stadiums.SID) left join fifa.goals on (fifa.starting_lineups.PlayerID = fifa.goals.PlayerID and fifa.starting_lineups.TeamID = fifa.goals.TeamID and fifa.goals.GameID = fifa.game.GameID) order by `FIFA Popular Name` ;"
cursor.execute(playerquery)
result = cursor.fetchall()

jsondoc = []

jsonobj = {"player" : result[0][0], "team" : result[0][1], "PlayerID" :result[0][5], "Position" : result[0][6], "Games" : []}
game = {"MatchDate": result[0][7], "City": result[0][8], "Stadium":result[0][9], "opposingTeam" : teamdict[result[0][3]] if (teamdict[result[0][2]] == result[0][1]) else teamdict[result[0][2]] }
jsonobj["Games"].append(game)
jsonobj["Goals"]=[]
a = result[0][10]
if(str(a) != 'None'):
    goal = {"Time":result[0][10],"MatchDate": result[0][7], "City": result[0][8], "Stadium":result[0][9], "opposingTeam" : teamdict[result[0][3]] if (teamdict[result[0][2]] == result[0][1]) else teamdict[result[0][2]]}
    jsonobj["Goals"].append(goal)
jsondoc.append(jsonobj)

k=0;
for i in range(0,len(result)-1,1):
    if(jsondoc[k]['player'] == result[i][0]):
        game = {"MatchDate": result[i][7], "City": result[i][8], "Stadium":result[i][9]}
        game["opposingTeam"] = teamdict[result[i][3]] if (teamdict[result[i][2]] == result[i][1]) else teamdict[result[i][2]] 
        jsondoc[k]["Games"].append(game)
        a = result[i][10]
        if(str(a) != 'None'):
            goal = {"Time":result[i][10],"MatchDate": result[i][7], "City": result[i][8], "Stadium":result[i][9], "opposingTeam" : teamdict[result[i][3]] if (teamdict[result[i][2]] == result[i][1]) else teamdict[result[i][2]]}
            jsondoc[k]["Goals"].append(goal)
    else:
        jsonobj = {"player" : result[i][0], "team" : result[i][1], "PlayerID" :result[i][5], "Position" : result[i][6]}
        jsonobj["Games"] = []
        game = {"MatchDate": result[i][7], "City": result[i][8], "Stadium":result[i][9]}
        game["opposingTeam"] = teamdict[result[i][3]] if (teamdict[result[i][2]] == result[i][1]) else teamdict[result[i][2]] 
        jsonobj["Games"].append(game)
        jsonobj["Goals"]=[]
        a = result[i][10]
        if(str(a) != 'None'):
            goal = {"Time":result[i][10],"MatchDate": result[i][7], "City": result[i][8], "Stadium":result[i][9], "opposingTeam" : teamdict[result[i][3]] if (teamdict[result[i][2]] == result[i][1]) else teamdict[result[i][2]]}
            jsonobj["Goals"].append(goal)
        jsondoc.append(jsonobj)
        k+=1
#print(jsondoc['playerData'])
playerdata_collection.insert(jsondoc)
    