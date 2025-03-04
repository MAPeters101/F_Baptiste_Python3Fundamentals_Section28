'''
Question 1
Use the pytz and dateutil libraries to convert this string into a UTC naive datetime object.

t = "Feb 8, 2021 5:30pm (Denver Time)"
Question 2
Use the requests library to load the following html page:

url = 'https://en.wikipedia.org/wiki/John_von_Neumann'
Once you have loaded that page, extract the title of that page, which is the text located between the <title> and </title> tags (often referred to as opening and closing tags, or start and end tags, respectively).

Hint: You'll want to read the Python docs for the find method available for strings:

https://docs.python.org/3/library/stdtypes.html?highlight=string#str.find

Question 3
Use a GET request to this URL:

url = 'https://httpbin.org/json'
Use the response from that request to:

determine the response format
extract the response into a Python object
Question 4
Use a POST request to call this url:

url = 'https://httpbin.org/anything'
Make this call passing the following query parameters: a=1 and b=2

Also, pass this dictionary as the body of the post request:

data = {
    'x': 100,
    'y': 200,
    'z': ['a', 'b', 'c']
}
Load the returned JSON into a Python object and print it out.
'''