import plotly.express as px
import plotly.graph_objects as go
import scipy.io as sio
import numpy as np
import pandas as pd


#issues
#would like to color groups more distinctly 
#want the df to hold group names instead of a numerical id for the group names
#want the animation to be faster or at least adjustable
#want to verify we have the x and y labeled right (pretty sure z is fine)
#eventually want a bar for the frame number

def load_from_mat(filename=None, data={}, loaded=None):
    '''Turn .mat file to nested dict of all values
    Pulled from https://stackoverflow.com/questions/62995712/extracting-mat-files-with-structs-into-python'''
    if filename:
        vrs = sio.whosmat(filename)
        #name = vrs[0][0]
        loaded = sio.loadmat(filename,struct_as_record=True)
        loaded = loaded["Data"]
    whats_inside = loaded.dtype.fields
    fields = list(whats_inside.keys())
    for field in fields:
        if len(loaded[0,0][field].dtype) > 0: # it's a struct
            data[field] = {}
            data[field] = load_from_mat(data=data[field], loaded=loaded[0,0][field])
        else: # it's a variable
            data[field] = loaded[0,0][field]
    return data

#Choices: working sample -> 'SampleData.mat' , one that is being worked on -> 'Mitchell_MocapData_Nairobi21.mat'
dat = load_from_mat('Mitchell_MocapData_Nairobi21.mat')
#dat = load_from_mat('SampleData.mat')

frames = []
labels = [] #name of points indexed in the same order the points are listed in df => labels[0] = df[0] has to be a better way to do this
for n, elem in enumerate(dat): 
    try: #last three dont seem to have markers?
        marker = dat[elem]
    except:
        break
    for i, point in enumerate(marker): #there is one less level of the arrays in the table, so take out previous "piece" for-loop, and move up its previous contents - Nick
        if len(frames) <= i:
            frames.append([])
        frames[i].append(np.append(point[0:len(point)], [n])) #x,y,z,frame#,seg_id 
        #Im not sure why, but [:-1] was only returning two out of three points - Nick
    labels.append(elem)


slider_dict = {
    'active': 0,
    'yanchor': 'top',
    'xanchor': 'left',
    'currentvalue': {
        'font': {'size': 18},
                 'prefix': "Frame",
                 'visible': False,
                 'xanchor': 'right'
    },
    'transition': {'duration': 300},
    'pad': {'b': 10, 't': 50},
    'len': 0.9,
    'x': 0.1,
    'y': 0,
    'steps': []
}

dfs = [] #will hold the df for each point indexed by frame#
for frame in frames:
    df = pd.DataFrame(frame)
    df.columns = ['X', 'Y', 'Z', 'Segment_ID']
    dfs.append(df)

    slider_step = {"args": [
        [frame],
        {"frame": {"duration": 300, "redraw": False},
         "mode": "immediate",
         "transition": {"duration": 300}}
    ],
        "label": df,
        "method": "animate"}
    slider_dict["steps"].append(slider_step)

#need:
#keys for slider


#all in plotly express but maybe we should use full library
#problems with this line
#keeps changing scale and the frame rate is crazy slow
#fig = px.scatter_3d(df, x='X', y='Y', z='Z', animation_frame='Frame', color='Group', range_x=[-5, 5], range_y=[-5, 5], range_z=[0, 5]) 

#full library attempt(unfinished)
#info for the axis scaling
#what should the xyz ranges be? Its gotta be fixed right?
x_min = -7
x_max = 7
y_min = -7
y_max = 7
z_min = 0
z_max = 7
scene_scaling = dict(xaxis = dict(range=[x_min, x_max], autorange=False),
                    yaxis = dict(range=[y_min, y_max], autorange=False),
                    zaxis = dict(range=[z_min, z_max], autorange=False),
                    aspectmode='cube')
#the figure (full library)
fig = go.Figure(
    data=[go.Scatter3d( x=dfs[0]['X'],
                        y=dfs[0]['Y'], 
                        z=dfs[0]['Z'],
                        mode='markers', #gets rid of line connecting all points
                        marker={'color':df['Segment_ID']},
                        hovertext= labels
                        ) #just for frame 1
    ],
    layout=go.Layout(width=800, height=800, #prob should change
                     scene = scene_scaling,
                     title="Sample", #change title
                     #slider= #the frame slider
                     sliders= slider_dict,
                     updatemenus=[dict(type="buttons",
                                        buttons=[dict(label="Play",
                                                    method="animate",
                                                    args=[None, {"fromcurrent": True, "frame": {"duration": 500, 'redraw': True}, "transition": {"duration": 0}}]), #i dont think this does anything but it should control the speedd https://plotly.com/javascript/animations/
                                                dict(label='Pause',
                                                     method="animate",
                                                     args=[[None], {"mode": "immediate"}]),
                                                dict(label="Restart",
                                                    method="animate",
                                                    args=[None, {"frame": {"duration": 500, 'redraw': True}, "mode": 'immediate',}]),
                                                ])]
    ),
    frames=[go.Frame(
            data= [go.Scatter3d(
                        x=df['X'],
                        y=df['Y'], 
                        z=df['Z'], 
                        mode='markers', #gets rid of line connecting all points
                        marker={'color':df['Segment_ID']},
                        connectgaps=False, #stops the filling in of blanks/NaNs
                        hovertext = labels
                        )])
            for df in dfs], #https://plotly.com/python-api-reference/generated/plotly.graph_objects.Figure.html
)


fig.update_layout(sliders=slider_dict)
fig.show()