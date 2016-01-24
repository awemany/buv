<!-- -*- mode: html -*- -->
% include("header.tpl", title="Member list "+obj.file_name)
%include("form_options.tpl", sha256=obj.sha256)
<h1>Member list</h1>

<ul>
% for member, addr in sorted(obj.iteritems()):
<li><div class="member_handle">{{member}}</div>:<div class="bitcoin_addr">{{addr}}</div></li>
% end
</ul>
% include("footer.tpl")    
