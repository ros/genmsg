
import os
import genmsg.msg_loader
import genmsg

# pkg_name - string
# msg_file - string full path
# search_paths -  dict of {'pkg':'msg_dir'}
def find_msg_dependencies(pkg_name, msg_file, search_paths):

    # Read and parse the source msg file                                                                                                     
    msg_context = genmsg.msg_loader.MsgContext.create_default() # not used?                                                                  
    full_type_name = genmsg.gentools.compute_full_type_name(pkg_name, os.path.basename(msg_file))
    spec = genmsg.msg_loader.load_msg_from_file(msg_context, msg_file, full_type_name)

    try:
        genmsg.msg_loader.load_depends(msg_context, spec, search_paths)
    except genmsg.InvalidMsgSpec as e:
        raise genmsg.MsgGenerationException("Cannot read .msg for %s: %s"%(full_type_name, str(e)))

    deps = set()
    for dep_type_name in msg_context.get_depends(full_type_name):
        deps.add( msg_context.get_file(dep_type_name) )

    return list(deps)


def find_srv_dependencies(pkg_name, msg_file, search_paths):

    # Read and parse the source msg file                                                                                        
    msg_context = genmsg.msg_loader.MsgContext.create_default() # not used?                                                      
    full_type_name = genmsg.gentools.compute_full_type_name(pkg_name, os.path.basename(msg_file))

    spec = genmsg.msg_loader.load_srv_from_file(msg_context, msg_file, full_type_name)

    try:
        genmsg.msg_loader.load_depends(msg_context, spec, search_paths)
    except genmsg.InvalidMsgSpec as e:
        raise genmsg.MsgGenerationException("Cannot read .msg for %s: %s"%(full_type_name, str(e)))

    deps = set()

    for dep_type_name in msg_context.get_depends(spec.request.full_name):
        deps.add( msg_context.get_file(dep_type_name) )

    for dep_type_name in msg_context.get_depends(spec.response.full_name):
        deps.add( msg_context.get_file(dep_type_name) )

    return list(deps)

#paths = {'std_msgs':'/u/mkjargaard/repositories/mkjargaard/dist-sandbox/std_msgs/msg'}
#file = '/u/mkjargaard/repositories/mkjargaard/dist-sandbox/quux_msgs/msg/QuuxString.msg'
#find_msg_dependencies('quux_msgs', file, paths)
