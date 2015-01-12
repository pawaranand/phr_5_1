frappe.provide("templates/includes");
frappe.provide("frappe");
{% include "templates/includes/inherit.js" %}
{% include "templates/includes/utils.js" %}
// {% include "templates/includes/form_generator.js" %}
{% include "templates/includes/list.js" %}
{% include "templates/includes/uploader.js" %}


SharePhr = function(){
	this.wrapper = '';
}

$.extend(SharePhr.prototype,{
	init:function(wrapper, args){
		console.log('test')
		this.wrapper = wrapper;
		this.args = args;
		var me = this;
		RenderFormFields.prototype.init(this.wrapper, {'fields':args['fields'], 
			'values': args['values']})
		console.log($('.field-area'))
		$('<div class="form-horizontal frappe-control" style="max-width: 600px;margin-top:10px;">\
			<div class="form-group row" style="margin: 0px">\
			<label class="control-label small col-xs-4" style="padding-right: 0px;">Share with</label>\
							<div class="col-xs-8">\
								<div class="control-input">\
									<input type="text" class="form-control" \
										placeholder="Email Id" name="share_with" \
										aria-describedby="basic-addon2">\
								</div>\
							</div>\
				</div>\
			</div>').appendTo($('.field-area'))
		$('<button id="share_data">Share Data</button></div>').appendTo($('.field-area'))
		$('<div class="event_section"></div>').appendTo($('.field-area'))
		$('#share_data').click(function(){
			me.send_email();
		})
		this.render_folder_section()
	 //  	me.bind_events()
	},
	render_folder_section:function(){
		var me = this;
		
		$("<div class='main' id='sharetab'></div>").appendTo($('.event_section'))
		
		folders = ['consultancy', 'event_snap', 'lab_reports', 'prescription', 'cost_of_care']
		// sub_folders = ['A', 'B', 'C']
		$('#sharetab').empty()

		console.log(this.args['selected_files'])

		if(this.args['selected_files']){
			console.log($.arrayIntersect(folders, this.args['selected_files']))
			folders = $.arrayIntersect(folders, this.args['selected_files'])
		}
		console.log(folders)
		$.each(folders, function(i, folder){
			$(repl_str('<div id = "%(id)s">\
				<div style = "display:inline-block;margin:5%; 5%;height:80px;text-align: center !important;"> \
		 			<i class="icon-folder-close-alt icon-large"></i> %(id)s <br> \
		 		</div>\
		 		<div class="btn btn-success" id = "A" \
		 			style = "display:inline-block;margin:5%; 5%;height:80px;text-align: center !important;"> \
		 			<i class="icon-folder-close-alt icon-large"></i> <br> A\
		 		</div>\
		 		<div class="btn btn-success" id = "B" \
		 			style = "display:inline-block;margin:5%; 5%;height:80px;text-align: center !important;"> \
		 			<i class="icon-folder-close-alt icon-large"></i> <br> B\
		 		</div>\
				<div class="btn btn-success" id = "B" \
		 			style = "display:inline-block;margin:5%; 5%;height:80px;text-align: center !important;"> \
		 			<i class="icon-folder-close-alt icon-large"></i> <br> C\
		 		</div>\
		 		</div>', {'id':folder})).appendTo(i==0?$('#sharetab'):$("#"+folders[i-1]))
		})		
		this.bind_sub_section_events()
	},
	bind_sub_section_events: function(){
		var me = this;
		$('#A, #B, #C').bind('click',function(){
				$("#sharetab").remove();
				$(repl_str("<li class='active'>%(parent)s</li><li class=active'>%(id)s</li>\
					",{'id':$(this).attr('id'), 'parent':$(this).parent().attr('id')})).appendTo('.breadcrumb');
				// $('.sharetab').empty();
				me.sub_folder = $(this).attr('id');
				me.folder = $(this).parent().attr('id')
				ThumbNails.prototype.init(me.wrapper, {'folder':me.folder, 
						'sub_folder':me.sub_folder, 'profile_id':'123456789', 'display':'initial'})
				// me.render_uploader_and_files();
			})	
	},
	send_email:function(){
		var me = this;
		var uniqueNames = [];

		$.each(me.selected_files, function(i, el){
			if($.inArray(el, uniqueNames) === -1) uniqueNames.push(el);
		});
		frappe.call({
			method:"phr.templates.pages.event.send_shared_data",
			args:{'files': uniqueNames, 'profile_id':'1420875549394-645191', 'folder':me.folder, 'sub_folder': me.sub_folder, 'share_with':$('input[name="share_with"]').val()},
			callback:function(r){
				frappe.msgprint("mail has been sent!!!")
			}
		})
	}

})