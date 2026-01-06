# training_recommender external API
Provides an API to see what the machine learning recommender has decided that an employee should take as their next training.

## Response sample
Response: will list recommended trainings in an array like the saved example in file recommender_response.json. The course_id field is important; it will point to a training. 

## How to invoke 
Request Path: /public/api/v1/mltr/v3/run
Request Verb: POST
Request Payload: will contain the employee_id in the ba_id field in the JSON like '{"data": {"ba_id":88563}}'

## Environment specific hostnames
Default is the lower environment value: https://dataiku-api-devqa.lower.internal.sephora.com
Productoin: https://dataiku-api-prod.prod.internal.sephora.com/public
