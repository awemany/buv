<!-- -*- mode: html -*- -->
% include("header.tpl", title="Prepare vote #2")

<h1>Select ballot option, handle and Bitcoin address</h1>
Voting on: {{proposal_meta.title}}

<form action="/prepare-vote" method="get">
  User handle voting:<br/>
  <input type="text" name="handle"/><br/>
  Bitcoin address voting:<br/>
  <input type="text" name="addr"/><br/>
  Ballot option<br/>
  <select name="ballot_option">
    %for bo in proposal_meta.ballot_options:
    <option value="{{bo}}">{{bo}}</option>
    %end
  </select>
  <input type="hidden" name="pm_hash" value="{{proposal_meta.sha256}}">
  <input type="submit" value="submit"><br/>
</form>

% include("footer.tpl")    
