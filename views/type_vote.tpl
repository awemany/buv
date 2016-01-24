<!-- -*- mode: html -*- -->
% include("header.tpl", title="Vote ("+obj.file_name+")")

<h1>Proposal meta data</h1>
<div>Handle: <b>{{obj.handle}}</b></div>
<div>Bitcoin address: <b>{{obj.addr}}</b></div>
<div>Signature: {{obj.signature}}</div>
<div>Voting with ballot option: <div class="ballot_option">{{obj.ballot_option}}</div></div>
<div>On proposal: <a href="/file-by-hash/{{obj.proposal.sha256}}">{{obj.proposal.file_name}}</a>, with meta data <a href="/formatted/{{obj.proposal_meta.sha256}}">{{obj.proposal_meta.file_name}}</a>, title "{{obj.proposal_meta.title}}".</div>
% include("footer.tpl")    
