Search.setIndex({docnames:["copyxnat","copyxnat.pyreporter","copyxnat.pyreporter.pyreporter","copyxnat.ui","copyxnat.ui.copyxnat_command_line","copyxnat.utils","copyxnat.utils.versioneer_version","copyxnat.utils.versioning","copyxnat.xnat","copyxnat.xnat.commands","copyxnat.xnat.copy_cache","copyxnat.xnat.run_command","copyxnat.xnat.xml_cleaner","copyxnat.xnat.xnat_interface","copyxnat.xnat_backend","copyxnat.xnat_backend.pyxnat_server","copyxnat.xnat_backend.server_factory","index","modules","versioneer"],envversion:{"sphinx.domains.c":2,"sphinx.domains.changeset":1,"sphinx.domains.citation":1,"sphinx.domains.cpp":3,"sphinx.domains.index":1,"sphinx.domains.javascript":2,"sphinx.domains.math":2,"sphinx.domains.python":2,"sphinx.domains.rst":2,"sphinx.domains.std":1,"sphinx.ext.viewcode":1,sphinx:56},filenames:["copyxnat.rst","copyxnat.pyreporter.rst","copyxnat.pyreporter.pyreporter.rst","copyxnat.ui.rst","copyxnat.ui.copyxnat_command_line.rst","copyxnat.utils.rst","copyxnat.utils.versioneer_version.rst","copyxnat.utils.versioning.rst","copyxnat.xnat.rst","copyxnat.xnat.commands.rst","copyxnat.xnat.copy_cache.rst","copyxnat.xnat.run_command.rst","copyxnat.xnat.xml_cleaner.rst","copyxnat.xnat.xnat_interface.rst","copyxnat.xnat_backend.rst","copyxnat.xnat_backend.pyxnat_server.rst","copyxnat.xnat_backend.server_factory.rst","index.rst","modules.rst","versioneer.rst"],objects:{"":{copyxnat:[0,0,0,"-"],versioneer:[19,0,0,"-"]},"copyxnat.pyreporter":{pyreporter:[2,0,0,"-"]},"copyxnat.pyreporter.pyreporter":{PyReporter:[2,1,1,""]},"copyxnat.pyreporter.pyreporter.PyReporter":{complete_progress:[2,2,1,""],info:[2,2,1,""],log:[2,2,1,""],message:[2,2,1,""],next_progress:[2,2,1,""],start_progress:[2,2,1,""],verbose_log:[2,2,1,""],warning:[2,2,1,""]},"copyxnat.ui":{copyxnat_command_line:[4,0,0,"-"]},"copyxnat.ui.copyxnat_command_line":{main:[4,3,1,""]},"copyxnat.utils":{versioneer_version:[6,0,0,"-"],versioning:[7,0,0,"-"]},"copyxnat.utils.versioneer_version":{NotThisMethod:[6,4,1,""],VersioneerConfig:[6,1,1,""],get_config:[6,3,1,""],get_keywords:[6,3,1,""],get_versions:[6,3,1,""],git_get_keywords:[6,3,1,""],git_pieces_from_vcs:[6,3,1,""],git_versions_from_keywords:[6,3,1,""],plus_or_dot:[6,3,1,""],register_vcs_handler:[6,3,1,""],render:[6,3,1,""],render_git_describe:[6,3,1,""],render_git_describe_long:[6,3,1,""],render_pep440:[6,3,1,""],render_pep440_old:[6,3,1,""],render_pep440_post:[6,3,1,""],render_pep440_pre:[6,3,1,""],run_command:[6,3,1,""],versions_from_parentdir:[6,3,1,""]},"copyxnat.utils.versioning":{get_version:[7,3,1,""],get_version_string:[7,3,1,""],version_from_pip:[7,3,1,""],version_from_versioneer:[7,3,1,""]},"copyxnat.xnat":{commands:[9,0,0,"-"],copy_cache:[10,0,0,"-"],run_command:[11,0,0,"-"],xml_cleaner:[12,0,0,"-"],xnat_interface:[13,0,0,"-"]},"copyxnat.xnat.commands":{Command:[9,1,1,""],CommandReturn:[9,1,1,""],check_datatypes_command:[9,3,1,""],check_datatypes_tostring:[9,3,1,""],command_factory:[9,3,1,""],commands:[9,3,1,""],copy_command:[9,3,1,""],count_command:[9,3,1,""],count_tostring:[9,3,1,""],export_command:[9,3,1,""],show_command:[9,3,1,""]},"copyxnat.xnat.copy_cache":{CacheBox:[10,1,1,""],CopyCache:[10,1,1,""]},"copyxnat.xnat.copy_cache.CacheBox":{new_cache:[10,2,1,""]},"copyxnat.xnat.copy_cache.CopyCache":{full_path:[10,2,1,""],sub_cache:[10,2,1,""],write_file:[10,2,1,""],write_xml:[10,2,1,""]},"copyxnat.xnat.run_command":{resolve_projects:[11,3,1,""],run_command:[11,3,1,""],run_command_on_servers:[11,3,1,""]},"copyxnat.xnat.xml_cleaner":{XmlCleaner:[12,1,1,""]},"copyxnat.xnat.xml_cleaner.XmlCleaner":{ATTR_SECONDARY_PROJECT_ID:[12,5,1,""],ICR_SUBJECT_ID_TAG:[12,5,1,""],MODALITY_TO_SCAN:[12,5,1,""],NAMESPACES:[12,5,1,""],TAGS_TO_DELETE:[12,5,1,""],TAGS_TO_REMAP:[12,5,1,""],XNAT_ASSESSORS_TAG:[12,5,1,""],XNAT_ASSESSOR_LABEL_ATTR:[12,5,1,""],XNAT_ASSESSOR_PROJECT_ATTR:[12,5,1,""],XNAT_CT_SCAN:[12,5,1,""],XNAT_EXPERIMENTS_TAG:[12,5,1,""],XNAT_FILE_TAG:[12,5,1,""],XNAT_IMAGE_SCAN_DATA_TAG:[12,5,1,""],XNAT_IMAGE_SESSION_ID:[12,5,1,""],XNAT_MODALITY_TAG:[12,5,1,""],XNAT_MR_SCAN:[12,5,1,""],XNAT_OTHER_SCAN:[12,5,1,""],XNAT_OUT_TAG:[12,5,1,""],XNAT_PREARCHIVE_PATH_TAG:[12,5,1,""],XNAT_PROJECT_ID_ATTR:[12,5,1,""],XNAT_PROJECT_NAME_TAG:[12,5,1,""],XNAT_RESOURCES_TAG:[12,5,1,""],XNAT_SCANS_TAG:[12,5,1,""],XNAT_SCAN_ID_ATTR:[12,5,1,""],XNAT_SESSION_ID_ATTR:[12,5,1,""],XNAT_SHARING_TAG:[12,5,1,""],XNAT_SUBJECT_ID:[12,5,1,""],XNAT_SUBJECT_ID_ATTR:[12,5,1,""],add_tag_remaps:[12,2,1,""],clean:[12,2,1,""],make_project_names_unique:[12,2,1,""],xml_from_string:[12,2,1,""]},"copyxnat.xnat.xnat_interface":{XnatAssessor:[13,1,1,""],XnatBase:[13,1,1,""],XnatExperiment:[13,1,1,""],XnatItem:[13,1,1,""],XnatParentItem:[13,1,1,""],XnatProject:[13,1,1,""],XnatReconstruction:[13,1,1,""],XnatResource:[13,1,1,""],XnatScan:[13,1,1,""],XnatServer:[13,1,1,""],XnatServerParams:[13,1,1,""],XnatSubject:[13,1,1,""]},"copyxnat.xnat.xnat_interface.XnatAssessor":{get_child_items:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatBase":{fetch_interface:[13,2,1,""],get_children:[13,2,1,""],user_visible_info:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatExperiment":{get_child_items:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatItem":{"export":[13,2,1,""],duplicate:[13,2,1,""],get_or_create_child:[13,2,1,""],run_recursive:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatParentItem":{"export":[13,2,1,""],clean:[13,2,1,""],duplicate:[13,2,1,""],get_child_items:[13,2,1,""],get_children:[13,2,1,""],get_resources:[13,2,1,""],get_xml:[13,2,1,""],get_xml_string:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatProject":{clean:[13,2,1,""],get_child_items:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatReconstruction":{get_child_items:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatResource":{"export":[13,2,1,""],duplicate:[13,2,1,""],get_children:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatScan":{get_child_items:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatServer":{datatypes:[13,2,1,""],get_children:[13,2,1,""],get_projects:[13,2,1,""],logout:[13,2,1,""],project:[13,2,1,""],project_list:[13,2,1,""]},"copyxnat.xnat.xnat_interface.XnatSubject":{get_child_items:[13,2,1,""]},"copyxnat.xnat_backend":{pyxnat_server:[15,0,0,"-"],server_factory:[16,0,0,"-"]},"copyxnat.xnat_backend.pyxnat_server":{PyXnatAssessor:[15,1,1,""],PyXnatExperiment:[15,1,1,""],PyXnatItem:[15,1,1,""],PyXnatItemWithResources:[15,1,1,""],PyXnatProject:[15,1,1,""],PyXnatReconstruction:[15,1,1,""],PyXnatResource:[15,1,1,""],PyXnatScan:[15,1,1,""],PyXnatServer:[15,1,1,""],PyXnatSubject:[15,1,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatAssessor":{create:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatExperiment":{create:[15,2,1,""],get_assessors:[15,2,1,""],get_reconstructions:[15,2,1,""],get_scans:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatItem":{create_on_server:[15,2,1,""],datatype:[15,2,1,""],fetch_interface:[15,2,1,""],get_xml_string:[15,2,1,""],label:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatItemWithResources":{create:[15,2,1,""],resources:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatProject":{create:[15,2,1,""],get_disallowed_project_ids:[15,2,1,""],subjects:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatReconstruction":{create:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatResource":{create:[15,2,1,""],create_on_server:[15,2,1,""],save_file:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatScan":{create:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatServer":{datatypes:[15,2,1,""],fetch_interface:[15,2,1,""],logout:[15,2,1,""],project:[15,2,1,""],project_list:[15,2,1,""],projects:[15,2,1,""]},"copyxnat.xnat_backend.pyxnat_server.PyXnatSubject":{create:[15,2,1,""],get_experiments:[15,2,1,""]},"copyxnat.xnat_backend.server_factory":{ServerFactory:[16,1,1,""]},"copyxnat.xnat_backend.server_factory.ServerFactory":{create:[16,2,1,""]},copyxnat:{pyreporter:[1,0,0,"-"],ui:[3,0,0,"-"],utils:[5,0,0,"-"],xnat:[8,0,0,"-"],xnat_backend:[14,0,0,"-"]},versioneer:{NotThisMethod:[19,4,1,""],VersioneerBadRootError:[19,4,1,""],VersioneerConfig:[19,1,1,""],do_setup:[19,3,1,""],do_vcs_install:[19,3,1,""],get_cmdclass:[19,3,1,""],get_config_from_root:[19,3,1,""],get_root:[19,3,1,""],get_version:[19,3,1,""],get_versions:[19,3,1,""],git_get_keywords:[19,3,1,""],git_pieces_from_vcs:[19,3,1,""],git_versions_from_keywords:[19,3,1,""],plus_or_dot:[19,3,1,""],register_vcs_handler:[19,3,1,""],render:[19,3,1,""],render_git_describe:[19,3,1,""],render_git_describe_long:[19,3,1,""],render_pep440:[19,3,1,""],render_pep440_old:[19,3,1,""],render_pep440_post:[19,3,1,""],render_pep440_pre:[19,3,1,""],run_command:[19,3,1,""],scan_setup_py:[19,3,1,""],versions_from_file:[19,3,1,""],versions_from_parentdir:[19,3,1,""],write_to_version_file:[19,3,1,""]}},objnames:{"0":["py","module","Python module"],"1":["py","class","Python class"],"2":["py","method","Python method"],"3":["py","function","Python function"],"4":["py","exception","Python exception"],"5":["py","attribute","Python attribute"]},objtypes:{"0":"py:module","1":"py:class","2":"py:method","3":"py:function","4":"py:exception","5":"py:attribute"},terms:{"1076c97":19,"1076c978a8d3cfc70f408fe5974aa6c092c949ac":19,"2001":12,"2021":17,"3176":19,"3615":19,"574ab98":19,"8601":19,"abstract":[10,13,15],"boolean":19,"case":19,"class":[2,6,9,10,12,13,15,16,19],"default":[6,11,19],"export":[9,13,19],"function":[5,6,7,9,13,19],"import":[17,19],"long":[6,19],"new":[10,13,15,19],"public":19,"return":[6,7,9,10,11,12,13,15,16,19],"short":[6,19],"static":[12,15,19],"throw":[7,19],"true":[9,11,12,13,16,19],"try":[6,19],"while":19,For:19,IDs:[12,15],The:[6,10,13,17,18],These:19,VCS:[6,19],__init__:19,__version__:19,_version:[6,19],abc:[13,15],about:19,absolut:[10,19],access:13,accur:19,action:[2,9],actual:19,add:[12,19],add_tag_remap:12,added:19,adding:19,addit:19,affect:17,after:[12,19],against:19,agnost:19,all:[9,11,13,19],allow:[11,13,15,19],along:19,alreadi:[6,12,13,15,19],also:[6,19],altern:19,alwai:[6,19],ambigu:[12,13],ani:19,anywai:[6,19],api:11,appear:[6,19],applic:4,appropri:[6,19],archiv:[6,17,19],arg:[4,6,19],argument:19,around:15,arrai:[11,13,15],ask:19,assembl:19,assessor:[12,13,15],attr_secondary_project_id:12,attr_to_tag_map:12,attribut:12,autom:19,avail:19,avoid:19,back:17,backend:[11,13,15,16],backward:[6,19],bar:2,base:[2,6,7,9,10,12,13,15,16,19],base_cach:13,base_nam:10,basic:19,becaus:15,been:[6,19],befor:[12,17,19],being:[15,19],below:19,between:[9,12,13,15,17,19],beyond:19,bind:19,both:[6,19],box:19,brian:19,browser:19,bug:19,build:[6,19],buildbot:19,cach:[10,11,13],cache_dir:11,cache_level:10,cache_typ:10,cachebox:10,call:[6,9,19],can:[9,13,15,17,19],cannot:15,captur:19,caus:19,caution:17,cc0:19,certain:19,certif:[11,16],cfg:19,chang:[11,12,13,19],check:[6,9,19],check_datatypes_command:9,check_datatypes_tostr:9,checkout:19,child:[10,13],children:13,choos:19,classmethod:15,clean:[6,12,13,19],cli:19,close:19,cmdclass:19,code:19,com:19,come:19,command:[0,4,6,8,11,19],command_factori:9,command_str:[9,11,17],commandreturn:9,commit:19,common:19,commonli:19,commun:[13,15,16],compar:19,compat:19,complet:[2,19],complete_progress:2,compliant:19,compon:19,comput:19,condens:19,config:19,configur:[6,19],conform:7,console_script:19,construct:[7,19],contain:[6,9,11,13,15,17,19],content:[9,13,17,18,19],continu:19,control:[10,19],conveni:19,convention:[6,19],convert:12,copi:[9,11,13,17],copy_cach:[0,8],copy_command:9,copycach:10,copyxnat_command_lin:[0,3],correct:[12,13,19],correctli:19,correspond:[6,13,19],could:19,count:9,count_command:9,count_tostr:9,covert:9,creat:[6,9,10,13,15,16,19],create_on_serv:15,creativ:19,creativecommon:19,ctscan:12,current:[6,15,19],custom:[2,19],cwd:[6,19],data:[9,11,13,17,19],databas:17,datatyp:[9,13,15],date:19,debug:[11,19],decor:[6,19],dedic:19,defin:[9,11],del:19,depend:19,describ:[6,7,12,19],descript:19,design:19,destin:[9,11,13,15],destination_par:13,detail:[17,19],determin:[6,19],dev0:[6,19],dev:17,devdist:[6,19],develop:19,dict:[9,12,19],dictionari:[9,12,19],differ:[11,13,19],direct:19,directori:[6,11,19],dirti:[6,19],disallow:15,disallowed_id:12,disallowed_nam:12,disconnect:[13,15],discuss:19,disk:[9,10,15],displai:[2,9,19],distanc:[6,19],distribut:19,distributionnotfound:19,distutil:19,do_setup:19,do_vcs_instal:19,document:17,doe:[13,15],doel:17,doesn:13,domain:19,don:[6,19],download:[11,17],dry_run:[2,11,13],dst:11,dst_host:11,dst_label:13,dst_project:9,dst_project_nam:11,dst_pw:11,dst_user:11,dst_xml_root:12,dst_xnat:9,dst_xnat_serv:11,duplic:13,dure:19,dynam:19,each:19,earlier:19,easi:19,easier:19,easili:19,edit:19,edu:12,egg_info:19,either:19,element:12,elementtre:12,els:[6,19],emb:19,embed:19,encapsul:13,end:2,enough:19,ensur:12,enter:17,entri:[4,19],entry_point:19,entrypoint:19,enumer:12,env:[6,19],equal:19,equival:19,error:19,etc:19,everi:19,exact:19,exactli:19,exampl:19,except:[6,7,19],execut:19,exist:[13,15],expand:[6,19],expect:19,experi:[12,13,15],export_command:9,extend:19,extract:[6,19],factori:[9,13,16],fail:19,fals:[2,6,10,11,13,19],fatal:19,featur:19,fetch:13,fetch_interfac:[13,15],file:[6,7,10,11,12,13,15,17,19],filenam:[10,19],find:[13,19],fix:[11,19],fix_scan_typ:[9,11,12,13],flavor:19,follow:19,form:[9,11],format:19,found:19,frequent:19,from:[6,11,13,15,19],from_par:[9,13],full:19,full_path:10,fulli:17,futur:19,g1076c97:19,g574ab98:19,gener:[17,19],get:[6,13,15,19],get_assessor:15,get_child_item:13,get_children:13,get_cmdclass:19,get_config:6,get_config_from_root:19,get_disallowed_project_id:15,get_experi:15,get_keyword:6,get_or_create_child:13,get_project:13,get_reconstruct:15,get_resourc:13,get_root:19,get_scan:15,get_vers:[6,7,19],get_version_str:7,get_xml:13,get_xml_str:[13,15],ghex:[6,19],git:[6,7,19],git_describ:[6,19],git_get_keyword:[6,19],git_pieces_from_vc:[6,19],git_versions_from_keyword:[6,19],gitattribut:19,github:19,give:19,given:[6,19],goal:[6,19],goe:19,handler:[6,19],happen:19,has:[9,19],hash:[6,19],hasn:[6,19],have:[6,17,19],head:19,help:[17,19],hex:[6,19],hide_stderr:[6,19],hierarchi:[10,13],homebrew:17,hopefulli:19,host:[13,16],hostnam:11,how:19,howev:19,http:[12,19],hub:17,human:9,icr:12,icr_subject_id_tag:12,idea:19,identifi:[6,13,19],ids:[13,15],imag:19,image_session_id:12,imagescandata:12,img:19,implement:[6,19],improv:19,includ:[6,15,19],incorrect:11,independ:19,index:17,indic:19,info:2,inform:[6,19],ini:19,initial_result:9,input:[9,11],insecur:[11,13,16],insid:[6,19],instal:19,instead:19,instruct:19,intend:17,interact:[11,17],interfac:[13,15],intermedi:19,investig:19,invok:19,ipi:19,iso:19,issu:19,item:[10,12,13,15],iter:2,its:[9,13,19],itself:19,jbweston:19,just:[6,19],kei:19,keyword:[6,19],know:19,known:19,label:[10,13,15],languag:19,later:[17,19],latest:[17,19],lead:17,learn:19,let:19,level:[6,10,13,19],librari:[11,19],licens:19,lightweight:19,like:[6,19],limit:19,line:4,list:[13,15,19],local:[6,9,13,19],local_fil:[13,15],log:[2,11],logic:19,logout:[13,15],look:[6,19],lookup:19,loss:17,maco:17,made:[11,13],mai:[11,17,19],main:[4,10,19],make:[13,17,19],make_project_names_uniqu:12,manag:19,mani:19,manifest_in:19,manual:19,map:12,mark:[6,19],marker:19,master:19,max_it:2,mayb:19,mean:[6,19],messag:2,method:[6,19],might:19,miniv:19,minver:19,miss:19,mit:17,modal:12,modality_to_scan:12,mode:[2,17,19],modern:19,modifi:[13,17],modul:[17,18],more:19,most:19,mostli:19,mrscan:12,multipl:19,must:19,myproject:19,name:[6,7,10,11,12,15,16,19],namespac:12,nbirn:12,necessari:19,need:[2,6,11,17,19],net:12,never:7,new_cach:10,newer:19,next:19,next_progress:2,nightli:19,node:13,non:[13,19],none:[4,6,9,10,11,13,17,19],note:[6,11,17,19],notthismethod:[6,19],nrg:12,number:[2,19],numpi:19,object:[2,6,9,10,11,12,13,15,16,19],old:19,older:[6,19],onc:19,one:[6,19],ones:19,onli:[2,6,19],onto:9,oper:[11,19],order:17,org:[12,19],other:[12,15,19],otherdicomscan:12,otherwis:19,our:[6,19],out:[6,12,19],output:[9,11,19],outputs_funct:9,outsid:19,overrid:19,overwrit:17,own:19,packag:[17,18,19],page:[17,19],param:[2,10,11,12,13,15,16],paramet:[6,13,15,19],parent:[6,13,15,19],parent_cach:13,parent_pyxnatitem:15,parent_rel_path:10,parentdir_prefix:[6,19],password:[11,16,17],past:19,path:[10,13,19],pep440:[7,19],perform:9,perhap:19,petscan:12,piec:[6,19],pip:19,pkg_resourc:19,place:[11,19],pleas:17,plus_or_dot:[6,19],point:[4,19],popul:6,post0:[6,19],post:[6,19],postdist:[6,19],postgresql:17,prearchivepath:12,prefix:[6,19],prereleas:17,presenc:19,present:[9,19],primarili:17,probabl:19,problem:19,proc:12,process:[4,11,19],produc:19,product:[7,17],progress:2,project:[6,9,11,12,13,15,17,19],project_filt:[11,17],project_list:[13,15],prompt:17,prone:19,proper:19,prov:12,provid:19,publicdomain:19,pull:19,purpos:19,pwd:13,pypa:19,pypi:[17,19],pypy3:19,pyreport:[0,11,17,18],python:[11,19],pyxnat:[11,15],pyxnat_serv:[0,14],pyxnatassessor:15,pyxnatexperi:15,pyxnatitem:15,pyxnatitemwithresourc:15,pyxnatproject:15,pyxnatreconstruct:15,pyxnatresourc:15,pyxnatscan:15,pyxnatserv:15,pyxnatsubject:15,quick:19,rais:[6,19],read:19,read_onli:[10,13],readabl:9,real:17,reason:19,rebuilt:19,recent:19,recommend:17,reconstruct:[15,19],record:19,recreat:19,recurs:9,reduc:19,regener:19,register_vcs_handl:[6,19],reimplement:19,relat:19,releas:[6,17,19],remap:12,remov:[12,19],render:[6,19],render_git_describ:[6,19],render_git_describe_long:[6,19],render_pep440:[6,19],render_pep440_old:[6,19],render_pep440_post:[6,19],render_pep440_pr:[6,19],replac:19,repo:7,report:[2,9,11,12,13,19],repres:10,represent:[13,15],request:[6,11,19],requir:[11,17,19],reset_funct:9,resolv:19,resolve_project:11,resourc:[12,13,15],result:[9,17,19],revis:19,revisionid:19,rewritten:[6,19],right:19,rocket:19,root:[6,12,19],root_path:10,roughli:19,run:[11,13,19],run_command:[0,6,8,17,19],run_command_on_serv:11,run_recurs:13,runtim:19,safe:7,same:19,save:[13,15],save_dir:15,save_fil:15,scan:[9,11,12,13,15],scan_setup_pi:19,scenario:[6,19],script:19,sdist:19,search:[6,17,19],secondari:[12,15],secondary_id:12,section:19,see:[17,19],select:19,self:[11,16,19],separ:19,server:[9,11,12,13,15,16,17],server_factori:[0,14],serverfactori:16,session:13,set:[11,12,19],setup:19,setuptool:19,setuptools_scm:19,sever:19,sha1:19,share:[12,19],shield:19,should:[11,13,19],shouldn:[6,19],show:[2,17],show_command:9,shown:13,sibl:19,side:19,sign:[11,16],signific:19,similar:19,single_project_filt:11,situat:19,slave:19,small:19,snapshot:19,softwar:[6,19],some:[10,11,19],someth:19,somewher:19,sort:[6,19],sourc:[2,4,6,7,9,10,11,12,13,15,16,17,19],special:19,specif:19,specifi:[11,13,19],src:[11,19],src_host:[11,17],src_project_nam:11,src_pw:[11,17],src_user:[11,17],src_xml_root:12,src_xnat_serv:11,start_progress:2,statu:[2,19],step:19,still:11,store:[10,11],str:13,string:[6,7,11,12,13,19],strip:19,style:[6,19],sub_cach:10,subclass:19,subdirectori:19,subject:[13,15],subject_id:12,subjectid:12,submodul:[0,18],subpackag:[17,18],subproject:19,subst:[6,19],substitut:19,suitabl:19,support:[6,19],sure:17,surpris:19,svg:19,system:[17,19],tag:[6,12,19],tag_prefix:[6,19],tags_to_delet:12,tags_to_remap:12,take:[11,19],tarbal:[6,19],tediou:19,tend:19,test:[11,19],text:19,than:[6,19],thei:15,them:19,theori:19,thi:[6,7,10,11,13,15,17,19],thing:19,those:19,through:19,time:19,to_children:9,tom:17,tomdoel:17,too:19,tool:[17,19],top:19,tostr:9,total:2,tox:19,track:19,transfer:12,travi:19,tree:[6,19],tri:19,two:[6,19],txt:17,type:[10,11,12,13],unabl:6,uncommit:19,uncondit:[6,19],under:[13,17,19],uniqu:[12,13,19],unknown:19,unpack:[6,19],unreleas:19,unsupport:19,untag:[6,19],updat:[12,19],upgrad:[17,19],upload:19,url:19,use:[12,13,15,17,19],used:[10,11,13,15,19],useful:[17,19],user:[2,7,11,13,16],user_visible_info:13,usernam:11,uses:[16,19],using:[11,15,19],usscan:12,usual:19,util:[0,18],valid:[6,19],valu:[9,12,13,19],variabl:9,variant:19,varieti:19,variou:19,vcs:[6,19],vendor:19,verbos:[2,6,11,19],verbose_log:2,verifi:19,version:[0,5,6,17,18],version_from_pip:7,version_from_version:7,versioneer_vers:[0,5],versioneerbadrooterror:19,versioneerconfig:[6,19],versionfile_ab:[6,19],versionfile_sourc:19,versions_from_fil:19,versions_from_parentdir:[6,19],virtualenv:19,visibl:[7,11],wai:19,warn:2,warner:19,web:19,went:19,were:[6,19],what:19,whatev:19,wheel:19,when:[11,17,19],where:[11,17,19],which:[9,13,15,19],whose:19,why:19,within:[10,19],without:[17,19],work:[17,19],wrap:[9,13],wrapper:[9,13,15],write:[10,11,19],write_fil:10,write_to_version_fil:19,write_xml:10,wrong:19,wustl:12,www:12,xdat:12,xml:[10,12,13,15],xml_cleaner:[0,8,13],xml_from_str:12,xml_root:[10,12,13],xml_string:12,xmlcleaner:12,xmlschema:12,xnat:[0,15,16,17,18],xnat_assessor_label_attr:12,xnat_assessor_project_attr:12,xnat_assessors_tag:12,xnat_backend:[0,17,18],xnat_ct_scan:12,xnat_experiments_tag:12,xnat_file_tag:12,xnat_image_scan_data_tag:12,xnat_image_session_id:12,xnat_interfac:[0,8],xnat_item:9,xnat_modality_tag:12,xnat_mr_scan:12,xnat_other_scan:12,xnat_out_tag:12,xnat_prearchive_path_tag:12,xnat_project_id_attr:12,xnat_project_name_tag:12,xnat_resources_tag:12,xnat_scan_id_attr:12,xnat_scans_tag:12,xnat_session_id_attr:12,xnat_sharing_tag:12,xnat_subject_id:12,xnat_subject_id_attr:12,xnat_typ:12,xnatassessor:13,xnatbas:13,xnatexperi:13,xnatinterfac:16,xnatitem:13,xnatparentitem:13,xnatproject:13,xnatreconstruct:13,xnatresourc:13,xnatscan:13,xnatserv:[11,13,15],xnatserverparam:13,xnatsubject:13,yield:19,you:[6,17,19],your:19,yourproject:19,zero:19},titles:["copyxnat package","copyxnat.pyreporter package","copyxnat.pyreporter.pyreporter module","copyxnat.ui package","copyxnat.ui.copyxnat_command_line module","copyxnat.utils package","copyxnat.utils.versioneer_version module","copyxnat.utils.versioning module","copyxnat.xnat package","copyxnat.xnat.commands module","copyxnat.xnat.copy_cache module","copyxnat.xnat.run_command module","copyxnat.xnat.xml_cleaner module","copyxnat.xnat.xnat_interface module","copyxnat.xnat_backend package","copyxnat.xnat_backend.pyxnat_server module","copyxnat.xnat_backend.server_factory module","CopyXnat","copyxnat","versioneer module"],titleterms:{The:19,api:17,author:17,code:17,command:[9,17],content:[0,1,3,5,8,14],copy_cach:10,copyright:17,copyxnat:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18],copyxnat_command_lin:4,develop:17,directli:17,docker:17,from:17,instal:17,licens:17,line:17,link:17,local:17,modul:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,19],own:17,packag:[0,1,3,5,8,14],pip:17,pyreport:[1,2],python:17,pyxnat_serv:15,quick:17,refer:17,run:17,run_command:11,server_factori:16,start:17,submodul:[1,3,5,8,14],subpackag:0,using:17,util:[5,6,7,17],version:[7,19],versioneer_vers:6,xml_cleaner:12,xnat:[8,9,10,11,12,13],xnat_backend:[14,15,16],xnat_interfac:13,your:17}})