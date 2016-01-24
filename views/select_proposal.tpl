<!-- -*- mode: html -*- -->
% include("header.tpl", title="Prepare vote")

<h1>Select proposal</h1>
<form action="/select-option" method="get">
  <select name="pm_hash">
    %for pm in proposal_metas:
    %if not pm.election:
    <option value="{{pm.sha256}}">{{pm.title}}</option>
    %end
    %end
  </select>
  <input type="submit" value="submit">
</form>

% include("footer.tpl")    
