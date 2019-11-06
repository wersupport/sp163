from wordpress_xmlrpc import Client, WordPressPost
from wordpress_xmlrpc.methods.posts import GetPosts, NewPost
from wordpress_xmlrpc.methods.users import GetUserInfo
from wordpress_xmlrpc import Client
from wordpress_xmlrpc.methods import posts

wp = Client('https://wersupport.com/xmlrpc.php', 'king001', 'king001002003!')




wp.call(GetUserInfo())


post = WordPressPost()
post.title = 'My new titlefdasf234'
post.content = 'This is the body of my new post.'
post.id = '123123'
post.terms_names = {
   'post_tag': ['test', 'firstpost'],
   'category': ['Introductions', 'Tests']
}

#publish a new post
post.post_status = 'publish'
wp.call(NewPost(post))