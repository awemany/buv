<!-- -*- mode: html -*- -->
% include("header.tpl", title="JSON for {{file_name}}")
% include("form_options.tpl", sha256=sha256)
    <h1>{{ file_name }}</h1>
    <pre>{{ !formatted_json }}</pre>

% include("footer.tpl")    
