<!-- -*- mode: html -*- -->
% include("header.tpl", title="List of proposals")

<h1>List of proposals and preliminary results</h1>

% for pm in proposal_metas:
<hr/>
<h2>Proposal {{pm.title}}</h2>
<div>Proposal link: <b><a href="/formatted/{{pm.proposal.sha256}}">{{pm.proposal.file_name}}</a></b>
<div>BU team voting:<b><a href="/formatted/{{pm.team.sha256}}">{{pm.team.file_name}}</a></b></div>
  % if len(pm.preliminary_tally):
<h3>Preliminary results</h3>
    % for option, count in pm.preliminary_tally.most_common():
<div><b>{{option}}</b> with <b>{{count}}</b> votes
    % end
    <ul>
    %for vote in pm.backref_votes:
    <li>{{vote.handle}}:{{vote.ballot_option}}</li>
    %end
    </ul>
  % end
% end  
% include("footer.tpl")    
