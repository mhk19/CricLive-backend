from time import sleep
import match_details
from pycricbuzz import Cricbuzz
import json
import websockets
import asyncio

run_types = {0: "dot", 1: "one", 2 : "two", 3 : "three", 4: "four", 6: "six"}

async def on_message(websocket, path):
    message = await websocket.recv()
    message = json.loads(message)
    if (message["type"] == "get_matches"):
        api_instance = Cricbuzz()
        matches = api_instance.matches()
        await websocket.send(json.dumps(matches))
    elif (message["type"] == "match_id"):
        api_instance = Cricbuzz()
        if (message["id"] == 'demo'):
            file = open('ind-vs-aus.json')
            data = json.load(file)
            match_info = data['match_info']
            livescore = data['livescore'][0]
            commentary = data['commentary']
        else:
            data = ''
            match_info = match_details.get_match_info(api_instance, message["id"])
            print(match_info)
            livescore = match_details.get_live_score(api_instance, message["id"])
            print(livescore)
            commentary = match_details.get_commentary(api_instance, message["id"])
        if commentary[0]['over']==None:
            striker = ''
            shot_type = ''
        else:
            striker = match_details.striker(commentary[0]['comm'])
            if (match_details.isStriker(striker, livescore['batting']['batsman'][0]['name'])):
                striker = livescore['batting']['batsman'][0]['name']
            else:
                striker = livescore['batting']['batsman'][1]['name']
            shot_type = match_details.findDirection(commentary[0]['comm'])
        json_object = json.dumps({"series": match_details.get_series_name(match_info),
                                    "team_names": match_details.get_team_names(match_info),
                                    "venue_names" : match_details.get_venue_name(match_info),
                                    "venue_location" : match_details.get_venue_location(match_info),
                                    "umpire" : match_details.get_umpire_name(match_info),
                                    "score" : {"runs": match_details.get_total_runs_of_batting_team(livescore),
                                                "wickets": match_details.get_total_wickets_of_batting_team(livescore),
                                                "overs" : match_details.get_total_overs(livescore),
                                                "inning" : match_details.get_inning_number(livescore),
                                                "batting_team" : match_details.get_batting_team_name(livescore),
                                                "bowling_team" : match_details.get_bowling_team_name(livescore),
                                                "batsman" : match_details.get_batsman(livescore),
                                                "bowler" : match_details.get_bowler(livescore),
                                                "striker": striker,
                                                "shot_type": shot_type
                                            },
                                })
        runs = int(match_details.get_total_runs_of_batting_team(livescore))
        overs = match_details.get_total_overs(livescore)
        wickets = int(match_details.get_total_wickets_of_batting_team(livescore))
        inning_num = match_details.get_inning_number(livescore)
        await websocket.send(json_object)
        if (message['id'] == 'demo'):
            for i in range(len(data['livescore'])-1):
                livescore = data['livescore'][i+1]
                if (match_details.get_total_overs(livescore) == overs and int(match_details.get_total_runs_of_batting_team(livescore))-runs == 1):
                    run_type = 'wide'
                elif inning_num == match_details.get_inning_number(livescore):
                    run_type = run_types[int(match_details.get_total_runs_of_batting_team(livescore))-runs]
                runs = int(match_details.get_total_runs_of_batting_team(livescore))
                overs = match_details.get_total_overs(livescore)
                inning_num = match_details.get_inning_number(livescore)
                if int(match_details.get_total_wickets_of_batting_team(livescore))-wickets != 0:
                    is_out = True
                    out_type = match_details.find_out_type(commentary[i+1]['comm'])
                    wickets = int(match_details.get_total_wickets_of_batting_team(livescore))
                else:
                    is_out = False
                    out_type = ''
                if commentary[i+1]['over'] == None:
                    striker = ''
                    shot_type = ''
                else:
                    striker = match_details.striker(commentary[i+1]['comm'])
                    if (match_details.isStriker(striker, livescore['batting']['batsman'][0]['name'])):
                        striker = livescore['batting']['batsman'][0]['name']
                    else:
                        striker = livescore['batting']['batsman'][1]['name']
                    shot_type = match_details.findDirection(commentary[i+1]['comm'])
                json_object = json.dumps({
                                            "score" : {"runs": match_details.get_total_runs_of_batting_team(livescore),
                                            "wickets": match_details.get_total_wickets_of_batting_team(livescore),
                                            "overs" : match_details.get_total_overs(livescore),
                                            "inning" : match_details.get_inning_number(livescore),
                                            "batting_team" : match_details.get_batting_team_name(livescore),
                                            "bowling_team" : match_details.get_bowling_team_name(livescore),
                                            "batsman" : match_details.get_batsman(livescore),
                                            "bowler" : match_details.get_bowler(livescore),
                                            "striker": striker,
                                            "shot_type": shot_type,
                                            "run_type": run_type,
                                            "is_out": is_out,
                                            "out_type": out_type,
                                        },
                })
                await websocket.send(json_object)
                sleep(2)
        else:
            over = match_details.get_total_overs(livescore)
            while(True):
                livescore = match_details.get_live_score(api_instance, message["id"])
                if (match_details.get_total_overs(livescore) != over):
                    over = match_details.get_total_overs(livescore)
                    commentary = match_details.get_commentary(api_instance, message["id"])
                    if commentary[0]['over']!=over:
                        striker = ''
                        shot_type = ''
                    else:
                        striker = match_details.striker(commentary[0]['comm'])
                        if (match_details.isStriker(striker, livescore['batting']['batsman'][0]['name'])):
                            striker = livescore['batting']['batsman'][0]['name']
                        else:
                            striker = livescore['batting']['batsman'][1]['name']
                        shot_type = match_details.findDirection(commentary[0]['comm'])
                    json_object = json.dumps({
                                                "score" : {"runs": match_details.get_total_runs_of_batting_team(livescore),
                                                "wickets": match_details.get_total_wickets_of_batting_team(livescore),
                                                "overs" : match_details.get_total_overs(livescore),
                                                "inning" : match_details.get_inning_number(livescore),
                                                "batting_team" : match_details.get_batting_team_name(livescore),
                                                "bowling_team" : match_details.get_bowling_team_name(livescore),
                                                "batsman" : match_details.get_batsman(livescore),
                                                "bowler" : match_details.get_bowler(livescore),
                                                "striker": striker,
                                                "shot_type": shot_type
                                            },
                    })
                    await websocket.send(json_object)


if __name__ == '__main__':
    start_server = websockets.serve(on_message, "localhost", 8765, ping_interval=None, ping_timeout=None)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
