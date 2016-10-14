import json
import os
import psycopg2
import psycopg2.extras
import web

import helper

urls = (

    # 0.0.0.0:8000/api/persona/
    "", "all_personas"
    
)
        
class all_personas:
    """ Extract all the personas.
    output:
        * persona.id
        * persona.name
        * persona.description
        * persona.type
        * workspace.id
        * workspace.url_name
        * default_vis in default_story in default_panel in default_workspace
    """
    def GET(self, connection_string=helper.get_connection_string(os.environ['DATABASE_URL'])):
        # connect to postgresql based on configuration in connection_string
        connection = psycopg2.connect(connection_string)
        # get a cursor to perform queries
        self.cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)    
        # execute query
        self.cursor.execute("""
            select distinct on (w.persona_id)
            w.id as workspace_id,
            w.url_name as workspace_url_name,
            p.id,
            p.name,
            p.description,
            pt.name as persona_type,
            pl.url_name as default_panel,
            vd.name as default_vis
            from """ + helper.table_prefix + """workspace w
            left join """ + helper.table_prefix + """persona p on p.id = w.persona_id
            left join """ + helper.table_prefix + """persona_type pt on pt.id = p.persona_type
            left join """ + helper.table_prefix + """workspace_panel wp on wp.workspace_id = w.id
            left join """ + helper.table_prefix + """panel pl on pl.id = wp.panel_id
            left join """ + helper.table_prefix + """persona_panel_story pps on pps.panel_id = wp.panel_id
            left join """ + helper.table_prefix + """story s on s.id = pps.story_id
            left join """ + helper.table_prefix + """vis v on v.id = s.vis_id
            left join """ + helper.table_prefix + """vis_directive vd on vd.id = v.vis_directive_id
            where w.is_default = true
            order by w.persona_id;
        """)
        # obtain the data
        data = self.cursor.fetchall()
        # close cursor and connection
        connection.close()
        self.cursor.close()
        # convert data to a string
        return json.dumps(data)

# instantiate the application
app = web.application(urls, locals())
