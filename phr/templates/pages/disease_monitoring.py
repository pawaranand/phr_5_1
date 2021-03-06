import frappe
import json
import os 
from frappe.utils import get_site_path, get_hook_method, get_files_path, get_site_base_path,cstr
from phr.templates.pages.patient import get_data_to_render
import datetime
from phr.templates.pages.patient import get_base_url
import time
from phr.phr.phr_api import get_response
from datetime import datetime

@frappe.whitelist(allow_guest=True)
def get_diseases():
	dt=frappe.db.sql("""select disease_name from `tabDisease Monitoring`""",as_list=1)
	return dt

@frappe.whitelist(allow_guest=True)
def get_disease_fields(name,profile_id=None):
	if name:
		dm=frappe.get_doc("Disease Monitoring",
			frappe.db.get_value("Disease Monitoring",{"disease_name":name},"name"))
		if dm:
			fields=[]
			rows=[]
			rows_raw=[]
			r=[]
			row_count=0
			r.append("")
			field_mapper=[]
			raw_fields=[]
			field_mapper.append("sr")
			for d in dm.get('parameters'):
				row_count+=1
				f_dic={"fieldname":d.fieldname,"fieldtype":d.fieldtype,"label":d.label}
				fields.append(f_dic)
				raw_fields.append(f_dic)
				r.append(d.label)
				field_mapper.append(d.fieldname)
				if row_count==4:
					row_count=0
					f_dic={"fieldname":"","fieldtype":"column_break","label":""}
					fields.append(f_dic)
					raw_fields.append(f_dic)
			s_break={"fieldname":"","fieldtype":"section_break","label":""}	
			fields.append(s_break)
			raw_fields.append(s_break)
			rows.append(r)
			rows_raw.append(r)	
			row_dic_raw={"fieldname":"tab","fieldtype": "table","label": "Disease Monitoring","rows":rows_raw}
			row_dic={"fieldname":"tab","fieldtype": "table","label": "Disease Monitoring","rows":rows}
			raw_fields.append(row_dic_raw)
			fields.append(row_dic)

			values=get_values(profile_id,fields,dm.event_master_id,field_mapper)
			return {
				"fields":fields, 
				"event_master_id":dm.event_master_id,
				"values":values,
				"field_mapper":field_mapper,
				"raw_fields":raw_fields
			}
	else:
		return 
		#values=get_existing_records_from_solr(profile_id,dm.event_master_id)

def get_values(profile_id,fields,event_master_id,field_mapper,raw_fields=None):
	res=get_existing_records_from_solr(profile_id,event_master_id)
	print res
	values=build_options(res,fields,field_mapper,raw_fields)
	return values

def get_existing_records_from_solr(profile_id,event_master_id):
	request_type="POST"
	url=get_base_url()+'getdiseasemtreventvisit'
	args={"profile_id":profile_id,"event_master_id":event_master_id}
	response=get_response(url,json.dumps(args),request_type)
	res=response.text
	if res:
		jsonobj=json.loads(res)
		if jsonobj["returncode"]==105:
			actdata=jsonobj["actualdata"]
			dmlist=json.loads(actdata)
			return dmlist[0]["disease_mtr_visit_List"]

def build_options(dm_list,fields,field_mapper,raw_fields=None):
	if isinstance(fields, list):
		f_list=fields
	else:
		frappe.errprint([raw_fields,"hiiii"])
		f_list=json.loads(raw_fields)
	pos=0
	for filed_dict in f_list:
		pos =+ 1
		if 'rows' in filed_dict.keys(): 
			rows = filed_dict.get('rows')
			break

	if dm_list:
		for dm in dm_list:
			v=[]
			f_dic={}
			
			for d in dm["data"]:
				val_list=d.split("=")
				f_dic[val_list[0]]=val_list[1]
			for f in field_mapper:
				#if not f=='patient_notes':
				if f=='sr':
					v.append("")
				else:
					v.append(f_dic[f])
			rows.extend([v])
	return f_list



@frappe.whitelist(allow_guest=True)
def save_dm(data,arg,fields,field_mapper,raw_fields):
	str_data=[]
	for key,value in json.loads(data).items():
		datastr=key+'='+value
		str_data.append(datastr)
	args=json.loads(arg)
	d=json.loads(data)
	args["data"]=str_data
	args["str_event_date"]=time.strftime('%d/%m/%Y')
	args["str_diseaseMonitoring_date"]=time.strftime('%d/%m/%Y')
	#args["str_diseaseMonitoring_date"]="09/01/2015"
	res=save_data_to_solr(json.dumps(args))
	values=get_values(args['profile_id'],fields,args['event_master_id'],json.loads(field_mapper),raw_fields) 
	return {
		"fields":values, 
		"event_master_id":args['event_master_id'],
		"values":values,
		"field_mapper":field_mapper
	}


def save_data_to_solr(args):
	request_type="POST"
	url=get_base_url()+'updatedismonitoring'
	response=get_response(url,args,request_type)
	res=response.text
	if res:
		jsonobj=json.loads(res)
		if jsonobj['returncode']==132 or jsonobj['returncode']==133:
			return "true"			
		else:
			return "false"	

@frappe.whitelist(allow_guest=True)
def render_table_on_db(profile_id,event_master_id,name):
	if name:
		data=get_disease_fields(name,profile_id)
		if data['values']:
			frappe.errprint(data['values'][len(data['values'])-1])
			return {
				"res_list":data['values'][len(data['values'])-1],
				"rtcode":1
			}


