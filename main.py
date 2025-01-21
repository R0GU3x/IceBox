import flet as ft
import core.firewall as firewall

class Rule(ft.UserControl):

    def __init__(self, rule:dict):
        super().__init__()
        self.rule = rule
        try:
            self.remote_port = rule['RemotePort']
        except:
            self.remote_port = 'xxxx'
        self.enabled = '#1cff1c' if rule['Enabled'] == 'Yes' else 'red'
        self.direction = 'images/in.png' if rule['Direction'] == 'In' else 'images/out.png'
        self.action = ('Allowed', '#1cff1c') if rule['Action'] == 'Allow' else ('Blocked', 'Orange')
    
    def build(self):

        def delete_rule(e):
            firewall.delete(self.rule)
            refresh_rule_list(0)

        rule_row = ft.Row(controls=[
            ft.Icon(name=ft.icons.SHIELD_SHARP, color=self.enabled), # enabled
            ft.Text(value=str(self.rule['Rule Name']).split(' ', 1)[-1]), # rule name
            ft.Row(controls=[
                ft.Image(src=self.direction, width=30, tooltip=self.rule['Direction']), # direction
                ft.Container(ft.Text(value=self.action[0]), 
                             border=ft.border.all(width=1, color=self.action[1]), 
                             border_radius=5, 
                             padding=ft.padding.symmetric(horizontal=10, vertical=2)),
                ft.Text(value=f"{self.rule['RemoteIP']}:{self.remote_port}"),
                ft.Text(value=f"{self.rule['Protocol']}"),
                ft.IconButton(ft.icons.DELETE_FOREVER_ROUNDED, icon_color='red',
                              on_click=delete_rule)
            ], spacing=25, alignment=ft.MainAxisAlignment.END),
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

        return ft.Container(rule_row, bgcolor='#60454545')

class NewRuleDialog(ft.UserControl):
    def __init__(self):
        super().__init__()

    def make_rule(self, e):
        status = 'Yes' if self.rule_status.value == 'Enable' else 'No'
        response = firewall.create_rule(name=f"[ICEBOX] {self.rule_name.value}", enable=status, action=self.rule_action.value, dir=self.rule_direction.value, protocol=self.rule_protocol.value, program=self.program.value, service=self.service.value, description=self.description.value, localip=self.local_ip.value, localport=self.local_port.value, remoteip=self.remote_ip.value, remoteport=self.remote_port.value)

        if response == 0:
            value, color = 'Firewall rule set successfully', '#1cff1c'
        elif response == 2:
            value, color = 'Administrator privileges required', 'red'
        else:
            value, color = response.strip('\n\r').split('\n')[0], 'yellow'

        self.response.value, self.response.color = value, color
        self.response.update()

        # print(response)
    
    def build(self):
        
        txt_style = ft.TextStyle(size=15, italic=True)

        # rule name
        self.rule_name = ft.TextField(label='Rule Name',
                                    label_style=txt_style,
                                    border_color='white')

        # rule status (eanbled / disabled)
        self.rule_status = ft.Dropdown(options=[
            ft.dropdown.Option('Enable'),
            ft.dropdown.Option('Disable')
        ], expand=True, border_color='white',
        label='Status',
        label_style=txt_style)

        # rule action (allow / block)
        self.rule_action = ft.Dropdown(options=[
            ft.dropdown.Option('Allow'),
            ft.dropdown.Option('Block'),
            ft.dropdown.Option('Bypass')
        ], expand=True, border_color='white',
        label='Action',
        label_style=txt_style)

        # rule direction (in / out)
        self.rule_direction = ft.Dropdown(options=[
            ft.dropdown.Option('In'),
            ft.dropdown.Option('Out')
        ], expand=True, border_color='white',
        label='Direction',
        label_style=txt_style)

        # rule protocol (tcp / udp / icmp)
        self.rule_protocol = ft.Dropdown(options=[
            ft.dropdown.Option('TCP'),
            ft.dropdown.Option('UDP'),
            ft.dropdown.Option('ICMP')
        ], expand=True, border_color='white',
        label='Protocol',
        label_style=txt_style)

        dd_row_1 = ft.Row(controls=[self.rule_status, self.rule_action], expand=True)
        dd_row_2 = ft.Row(controls=[self.rule_direction, self.rule_protocol])

        dd_main_col = ft.Column(controls=[dd_row_1, dd_row_2])

        self.description = ft.TextField(label='Description',
                                    label_style=txt_style,
                                    border_color='white')
        
        self.program = ft.TextField(label='Program',
                                    label_style=txt_style,
                                    border_color='white')
        
        self.service = ft.TextField(label='Service',
                                    label_style=txt_style,
                                    border_color='white')
    
        self.local_ip = ft.TextField(label='Local IP address',
                                    label_style=txt_style,
                                    hint_text='0.0.0.0',
                                    hint_style=txt_style,
                                    border_color='white',
                                    expand=True)
        self.local_port = ft.TextField(label='Local Port',
                                    label_style=txt_style,
                                    hint_text='1234',
                                    hint_style=txt_style,
                                    border_color='white',
                                    expand=True)
        
        self.remote_ip = ft.TextField(label='Remote IP address',
                                    label_style=txt_style,
                                    hint_text='0.0.0.0',
                                    hint_style=txt_style,
                                    border_color='white',
                                    expand=True)
        self.remote_port = ft.TextField(label='Remote Port',
                                    label_style=txt_style,
                                    hint_text='1234',
                                    hint_style=txt_style,
                                    border_color='white',
                                    expand=True)

        ip_local_row = ft.Row(controls=[self.local_ip, self.local_port])
        ip_remote_row = ft.Row(controls=[self.remote_ip, self.remote_port])

        ip_main_column = ft.Column(controls=[ip_local_row, ip_remote_row])

        self.response = ft.Text(size=15)

        main_column = ft.Column(controls=[
            self.rule_name,
            dd_main_col,
            self.program,
            self.service,
            self.description,
            ip_main_column,
            self.response
        ], width=PAGE.width, height=PAGE.height)

        return ft.Container(main_column)

title = ft.Container(ft.Text("ICE BOX", font_family=2, size=60), padding=ft.padding.only(bottom=50))

def search(e):
    # response = firewall.search(e.data)
    response = firewall.search(search_box.value)
    rules_listView.controls = [Rule(rule) for rule in response]
    PAGE.update()


search_box = ft.TextField(border_color='#ffffff', 
                            hint_text='enter your search keyword here...', 
                            hint_style=ft.TextStyle(color='#a3a3a3', 
                                                    font_family='SimSun'),
                            border_radius=30,
                            expand=True, on_submit=search,
                            text_align=ft.TextAlign.CENTER)


def add_new_rule(e):
    nrd = NewRuleDialog()

    new_rule_dialog = ft.AlertDialog(
        modal=True, 
        title=ft.Text(value='New Rule'),
        content=nrd,
        actions=[ft.Row(controls=[
            ft.ElevatedButton(text='Cancel', on_click=lambda e: PAGE.close(new_rule_dialog), color='Red'),
            ft.ElevatedButton(text='Create', on_click=nrd.make_rule, color='#1cff1c')
        ], alignment=ft.MainAxisAlignment.END)],
        shadow_color=ft.colors.BLACK)
    
    # PAGE.add(new_rule_dialog)
    PAGE.open(new_rule_dialog)
    PAGE.update()

new_button = ft.ElevatedButton(icon=ft.icons.ADD, text='New', 
                               color='#1cff1c', 
                               style=ft.ButtonStyle(side=ft.BorderSide(width=1, color='#1cff1c')),
                               on_click=add_new_rule)
row2 = ft.Row(controls=[search_box, new_button])

RULES = None

def refresh_rule_list(e):
    # refreshing
    refresh_button.icon_color = 'yellow'
    PAGE.update()
    rules_listView.visible = False
    PAGE.update()

    global RULES
    RULES = firewall.show_rules()
    rules_listView.controls = [Rule(rule) for rule in RULES]
    rules_listView.scroll = ft.ScrollMode.AUTO
    PAGE.update()

    # refresh completed
    refresh_button.icon_color = '#00ffff'
    PAGE.update()
    rules_listView.visible = True
    PAGE.update()


refresh_button = ft.IconButton(icon=ft.icons.REFRESH_ROUNDED, icon_color='#00ffff', icon_size=25, 
                                            # style=ft.ButtonStyle(side=ft.BorderSide(width=1, color='#008282')),
                                            on_click=refresh_rule_list)
refresh_container = ft.Container(refresh_button, margin=ft.margin.only(right=20))

# FILTER CHECK BOXES

def toggle_filter(e):
    
    search_box.value = filter_radio.value

    search(search_box.event_handlers)
    PAGE.update()

# make a radio button
filter_radio = ft.RadioGroup(ft.Row(controls=[
    ft.Radio(label="All", value=''),
    ft.Radio(label="Icebox", value='icebox'),
    ft.Radio(label="Allowed", value='allow'),
    ft.Radio(label="Blocked", value='block'),
    ft.Radio(label="TCP", value='tcp'),
    ft.Radio(label="UDP", value='udp'),
]), on_change=toggle_filter)

filter_radio.value = 'icebox'

refersh_filter_row = ft.Row(controls=[filter_radio, refresh_container],
                            alignment=ft.MainAxisAlignment.SPACE_BETWEEN)

rules_listView = ft.ListView(cache_extent=30, reverse=True, spacing=2, expand=True)
rules_container = ft.Container(rules_listView, border_radius=10)
rules_column = ft.Column(controls=[refersh_filter_row, rules_container], 
                         expand=True, 
                         horizontal_alignment=ft.CrossAxisAlignment.END,
                         scroll=ft.ScrollMode.AUTO)

home_page = ft.Column(controls=[title, row2, rules_column],
    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    expand=True
)

def main(page: ft.Page):
    page.fonts = {
        1:"fonts/RAINED PERSONAL USE.ttf",
        2:"fonts/HotSweat.ttf"
    }
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    global PAGE
    PAGE = page

    page.add(home_page)

    refresh_rule_list(0)

ft.app(main)