<!-- -*- mode: html -*- -->
% include("header.tpl", title="Completed election "+obj.file_name)
%include("form_options.tpl", sha256=obj.sha256)
<h1>Completed election</h1>
<div>Election for proposal: <a href="/formatted/{{obj.proposal.sha256}}">{{ obj.proposal_hash }}, {{ obj.proposal.file_name }}</a></div>
<div>With meta data: <a href="/formatted/{{obj.proposal_meta.sha256}}">{{ obj.proposal_meta_hash }}, {{ obj.proposal_meta.file_name }}</a></div>
List of votes:
<ul>
% for v in obj.vote:
<li>
  <a href="/formatted/{{v.sha256}}">{{v.file_name }}</a>
</li>  
% end
</ul>


% include("footer.tpl")    
