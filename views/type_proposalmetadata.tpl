<!-- -*- mode: html -*- -->
% include("header.tpl", title="Proposal meta data "+obj.file_name)
%include("form_options.tpl", sha256=obj.sha256)
<h1>Proposal meta data</h1>
<div>Title of proposal: <b>{{obj.title}}</b></div>
<div>Proposal link: <b><a href="/formatted/{{obj.proposal.sha256}}">{{obj.proposal.file_name}}</a></b>
<div>BU team voting:<b><a href="/formatted/{{obj.team.sha256}}">{{obj.team.file_name}}</a></b></div>
<div>This proposal, if accepted, will supersede the following proposal(s):
% for s in obj.supersede:  
  <b>{{s.sha256}} </b>
% end  
</div>
<div>Voting on this proposal implicitely accepts the results of the following elections:
% for c in obj.confirm:  
  <b>{{c.sha256}} </b>
% end  
</div>
<div>The options on the ballot are:<b>{{obj.ballot_options}}</b><div>
<div>The election is validating using all of the following methods:<b>{{obj.voting_methods}}</b></div>
% include("footer.tpl")    
