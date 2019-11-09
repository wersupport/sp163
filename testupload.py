from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts,taxonomies

import mimetypes



client = Client('https://wersupport.com/xmlrpc.php', 'king001', 'king001002003!')

# set to the path to your file
filename = '1天猫-网店.png'

# prepare metadata
data = {
        'name': 'picture.jpg',
        'type': mimetypes.guess_type(filename)[0],  # mimetype
}

# read the binary file and let the XMLRPC library encode it into base64
with open(filename, 'rb') as img:
        data['bits'] = xmlrpc_client.Binary(img.read())

response = client.call(media.UploadFile(data))
# response == {
#       'id': 6,
#       'file': 'picture.jpg'
#       'url': 'http://www.example.com/wp-content/uploads/2012/04/16/picture.jpg',
#       'type': 'image/jpeg',
# }
attachment_id = response['id']
print(attachment_id)


post = WordPressPost()
tm=taxonomies.GetTaxonomy('seo')
print(tm)
post.title = 'Picture of the Dayfdasf'
post.content = 'What a lovely picture today!'
post.post_status = 'publish'
post.thumbnail = attachment_id
post.id = client.call(posts.NewPost(post))



