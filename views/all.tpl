<!-- -*- mode: html -*- -->
% include("header.tpl", title="Item list")

<h1>List of all items in vote chain</h1>
<ul>
% for item, sha256  in items:
<li><pre>{{item.file_name}} [<a href="/formatted/{{sha256}}">{{sha256}}</a>]</pre></li>
% end
</ul>
% include("footer.tpl")    
