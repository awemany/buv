<!-- -*- mode: html -*- -->
% include("header.tpl", title="Prepare and sign vote")
<h1>Prepare and sign vote</h1>

<div>Handle:{{handle}}</div>
<div>Address:{{addr}}</div>
<div>Voting:{{ballot_option}}</div>
<div>On:{{proposal_meta.sha256}}, {{proposal_meta.proposal.sha256}}</div>
<div>
  <b>After double-checking that the following hashes are correct</b>, please sign the following text using your Bitcoin client:

  <font size="1"><pre>VOTE-FORMAT-VERSION-1 {{handle}} {{addr}} {{ballot_option}} {{proposal_meta.proposal.sha256}} {{proposal_meta.sha256}}</pre></font>
    
  Put the signature here, and click submit:
  <form action="/submit-vote" method="post">
    <input type="hidden" name="handle" value="{{handle}}">
    <input type="hidden" name="addr" value="{{addr}}">
    <input type="hidden" name="ballot_option" value="{{ballot_option}}">
    <input type="hidden" name="proposal_hash" value="{{proposal_meta.proposal.sha256}}">
    <input type="hidden" name="proposal_meta_hash" value="{{proposal_meta.sha256}}">
    <input type="text" name="signature"></br>
    <input type="submit">
    </form>
</div>
% include("footer.tpl")    
