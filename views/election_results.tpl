<!-- -*- mode: html -*- -->
% include("header.tpl", title="List of elections")

<h1>Election results</h1>

% for election in elections:
<h2>Election for proposal {{election.proposal_meta.title}}</h2>
<div>Proposal file, meta file: <b>{{election.proposal.file_name}},  {{election.proposal_meta.file_name}}</b></div>
% if election.result.valid:
  <div>Election is <b>valid</b></div>
% else:
  <div>Election is <b>invalid</b></div>
% end  
<div>Elected ballot option:<b>{{election.result.voted_option}}</b></div>
<div>Comments from vote counting:
% for comment in election.result.comments:
  <b>{{comment}} </b>
% end
</div>
% end
% include("footer.tpl")    
