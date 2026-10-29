# ID reference bookkeeping is not shading content. Retain all actual node/property data.
_raw_node_data=node_data
def node_data(datablock):
 data=_raw_node_data(datablock)
 for k in ['users','use_fake_user','is_updated','is_updated_data','is_updated_transform']:
  data['props'].pop(k,None)
 return data
