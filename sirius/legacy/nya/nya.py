'''
from graia.saya import Saya, Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.application import GraiaMiraiApplication
from graia.application.event.messages import *
from graia.application.event.mirai import *
from graia.application.message.elements.internal import Image
from modules.tools.IsCommand import IsCommand

import requests
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = "2"
from imageai.Classification import ImageClassification

# 插件信息
__name__ = "Nya"
__description__ = "猫图检测"
__author__ = "SinceL"
__usage__ = "自动使用"

saya = Saya.current()
channel = Channel.current()

channel.name(__name__)
channel.description(f"{__description__}")
channel.author(__author__)

bcc = saya.broadcast

prediction = ImageClassification()
prediction.setModelTypeAsResNet50()
modelpath = os.getcwd() + '/modules/tools/nya/models/resnet50_imagenet_tf.2.0.h5'
prediction.setModelPath(modelpath)
prediction.loadModel()

'''
'''
@channel.use(ListenerSchema(listening_events=[GroupMessage]))
async def group_message_listener(
    app: GraiaMiraiApplication,
    message: MessageChain,
    sender: Member,
    group: Group
):
    if IsCommand(message):
        return
    picList = message.get(Image)
    if len(picList) == 0:
        return
    else:
        await PredictImage(picList, app, group)


def GetImage(picture: Image):
    url = picture.url
    filename = picture.imageId
    data = requests.get(url).content
    address = os.getcwd() + '/modules/tools/nya/cache/' + filename
    with open(address, 'wb') as file:
        file.write(data)
        file.close()
    return address


async def PredictImage(images: [Image], app, group):
    ret = []
    cat = False
    for picture in images:
        picture: Image
        address = GetImage(picture)
        print('看看猫')
        predictions, probabilities = prediction.classifyImage(address, result_count=10)
        print(predictions)
        for name in predictions:
            if 'cat' in name or 'tabby' in name:
                ret.append(picture)
                cat = True
                break
    if cat:
        await app.send_group_message(group, MessageChain(ret))
    return
'''
