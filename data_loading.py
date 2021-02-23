# 1 import required libraries
import json
from csv import writer
#from apiclient.discovery import build
from googleapiclient.discovery import build
import os
from urllib.parse import urlparse, parse_qs

# ulr_parser
def get_id(url):
    u_pars = urlparse(url)
    quer_v = parse_qs(u_pars.query).get('v')
    if quer_v:
        return quer_v[0]
    pth = u_pars.path.split('/')
    if pth:
        return pth[-1]

# configure function parameters for required variables to pass to service
def get_comments(part='snippet',
                 maxResults=100,
                 textFormat='plainText',
                 order='time',
                 videoId=get_id(input('Input link:')),
                 csv_filename=input('Enter file name:')):
    # create empty lists to store desired information
    comments, commentsId, repliesCount, likesCount, viewerRating = [], [], [], [], []

    # build our service from path/to/apikey
    api_key = os.environ.get('api_key')
    service = build('youtube', 'v3', developerKey=api_key)


    # make an API call using our service
    response = service.commentThreads().list(
        part=part,
        maxResults=maxResults,
        textFormat=textFormat,
        order=order,
        videoId=videoId
    ).execute()

    while response:  # this loop will continue to run until you max out your quota

        for item in response['items']:
            # index item for desired data features
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comment_id = item['snippet']['topLevelComment']['id']
            reply_count = item['snippet']['totalReplyCount']
            like_count = item['snippet']['topLevelComment']['snippet']['likeCount']

            # append to lists
            comments.append(comment)
            commentsId.append(comment_id)
            repliesCount.append(reply_count)
            likesCount.append(like_count)
            # write line by line
            with open(f'{csv_filename}.csv', 'a+', encoding="utf-8") as f:
                # https://thispointer.com/python-how-to-append-a-new-row-to-an-existing-csv-file/#:~:text=Open%20our%20csv%20file%20in,in%20the%20associated%20csv%20file
                csv_writer = writer(f)
                csv_writer.writerow([comment, comment_id, reply_count, like_count])

        # check for nextPageToken, and if it exists, set response equal to the JSON response
        if 'nextPageToken' in response:
            response = service.commentThreads().list(
                part=part,
                maxResults=maxResults,
                textFormat=textFormat,
                order=order,
                videoId=videoId,
                pageToken=response['nextPageToken']
            ).execute()
        else:
            break
    print('Done')
    print('Count of comments loaded:',len(comments)+sum(repliesCount))
    # return our data of interest
    return {
        'Comments': comments,
        'Comment ID': commentsId,
        'Reply Count': repliesCount,
        'Like Count': likesCount
    }

get_comments()
