import scrapy
import pickle
import re

from ..items import AlbumItem

class AlbumsSpider(scrapy.Spider):
    name = "album"

    download_delay = 3

    def start_requests(self):
        url = "https://www.discogs.com/sell/list?sort=price%2Cdesc&limit=250&style=Gospel&page="
        pageAmountAfterFirst = 16
        for i in range(1, pageAmountAfterFirst):
            yield scrapy.Request(url=url+str(i), callback=self.parse)

    def parse(self, response):
        # page = response.url.split("/")[-2]
        # filename = 'testpage%s.html' % page
        # with open(filename, 'wb') as f:
        #     f.write(response.body)

        # self.log('saved file %s' % filename)

        # smallPercentBetter = have/want * 100

        maxPercent = 30

        albums = response.xpath("//tr[@class='shortcut_navigable ']")

        albumsDict = {}

        for HTMLblock in albums:
            converted = self.convertToDict(HTMLblock)

            if (converted is None 
                or converted['releaseId'] in albumsDict 
                or converted['name'] in albumsDict
                or not self.filterTheAlbums(converted, maxPercent)):
                continue
            
            albumsDict[converted['releaseId']] = converted

        # transformedAlbum = list(filter(None, (self.convertToDict(HTMLblock) for HTMLblock in albums)))
    
        # gettingRareButGood = [album for album in transformedAlbum if self.filterTheAlbums(album, maxPercent)]

        style = self.getTheStyle(response.url)
        
        items = AlbumItem()

        for el in albumsDict.keys():

            items['name'] = albumsDict[el]['name']
            items['releaseId'] = albumsDict[el]['releaseId']
            items['have'] = int(albumsDict[el]['have'])
            items['want'] = int(albumsDict[el]['want'])
            items['price'] = int(albumsDict[el]['price'])
            items['style'] = style

            yield items

        # print("transformedAlbum ", transformedAlbum)

        # Album.objects.bulk_create(transformedAlbum)

        # filehandler = open(b"processedAlbums", "wb")

        # pickle.dump(filterAlbums, filehandler)

        # filehandler.close()



    def convertToDict(self, htmlBlock):
        #filterAlbums = [ ok for ok in transformedAlbum if ok is not None and self.filterTheAlbums(ok, maxPercent)]

        _, name, _, releaseId = htmlBlock.css(".item_release_link::attr(href)").extract()[0].split('/')

        communityStats = htmlBlock.css(".community_label::text").extract()
        if len(communityStats) < 2:
            return

        have, want = htmlBlock.css(".community_label::text").extract()

        price = self.getRelevantPrice(htmlBlock)

        return { "name": name, "releaseId": releaseId, "price": price, 
                 "have": have.split(' ')[0], "want": want.split(' ')[0] }



    def convertToModel(self, htmlBlock, maxPercent):
        #extract data
        _, name, _, releaseId = htmlBlock.css(".item_release_link::attr(href)").extract()[0].split('/')

        communityStats = htmlBlock.css(".community_label::text").extract()
        if len(communityStats) == 1:
            return
        haveRaw, wantRaw = htmlBlock.css(".community_label::text").extract()

        have = int(have.split(' ')[0])

        want = int(want.split(' ')[0])

        if (have/want * 100) < 30:
            return

        return Album(name=name, releaseId=releaseId, have=have, want=want)


    def filterTheAlbums(self, albumData, percentage):
        return (int(albumData['have'])/int(albumData['want']) * 100) < percentage

    def getTheStyle(self, url):
        splitURL = url.split('&')
        # ['discogs.com/', 'limit=25', 'style=Soul+Vibe', 'page=1']
        for text in splitURL:
            if "style" in text:
                # 'style=Soul+Vibe' -> 'Soul Vibe'
                return text.split('=')[-1].replace('+',' ')

    def getRelevantPrice(self, htmlBlock):
        convertedToLocalCurrency = htmlBlock.css(".converted_price::text").extract()
        
        tempPriceString = ''

        if len(convertedToLocalCurrency) > 0: 
            tempPriceString += convertedToLocalCurrency[0]
        else:
            tempPriceString += htmlBlock.css(".price").extract()[0]
        
        # $7,594.92 -> 759492
        return re.sub("[^0-9]", "", tempPriceString.strip())

        

#>>> response.css(".community_label::text").extract()[2]  
#'31 want'

# >>> response.css(".item_release_link::attr(href)").extract()[0].split('/')    
# ['', 'Prince-The-Black-Album', 'release', '11276350']

# albums = response.xpath("//tr[@class='shortcut_navigable ']")   

# block.css(".item_release_link::attr(href)").extract()[0].split('/')

# block.css(".community_label::text").extract()  

# def convertToDict(htmlBlock):
#     #extract data
#     _, name, _, releaseID = htmlBlock.css(".item_release_link::attr(href)").extract()[0].split('/')

#     communityStats = htmlBlock.css(".community_label::text").extract()
#     if len(communityStats) == 1:
#         return
#     have, want = htmlBlock.css(".community_label::text").extract()
#     return { "name": name, "releaseID": releaseID, "have": have.split(' ')[0], "want": want.split(' ')[0] }

# [ convertToDict(block) for block in albums ]

# albumData = {}

# for block in albums:
#     _, name, _, releaseID = block.css(".item_release_link::attr(href)").extract()[0].split('/')
#     if releaseID in albumData:
#         continue
#     communityStats = block.css(".community_label::text").extract()
#     if len(communityStats) == 1:
#         continue
#     have, want = communityStats
#     albumData[releaseID] = { "name": name, "releaseID": releaseID, "have": have.split(' ')[0], "want": want.split(' ')[0] }


# {'name': 'Prince-The-Black-Album', 'releaseID': '11276350', 'have': '64', 'want': '607'}, 
# {'name': 'Adiam-Black-Wedding', 'releaseID': '9250701', 'have': '19', 'want': '8'}, 
# {'name': 'Prince-The-Black-Album', 'releaseID': '2031147', 'have': '438', 'want': '1299'}, 
# {'name': 'The-Brief-Encounter-Introducing-The-Brief-Encounter', 'releaseID': '1595967', 'have': '43', 'want': '1250'}, 
# {'name': 'Rita-The-Tiaras-Gone-With-The-Wind-Is-My-Love', 'releaseID': '14021652', 'have': '4', 'want': '64'}, 
# {'name': 'James-Brown-The-Payback', 'releaseID': '804277', 'have': '505', 'want': '579'}, 
# {'name': 'Brooklyn-Dreams-Brooklyn-Dreams', 'releaseID': '7206882', 'have': '25', 'want': '23'}, 
# {'name': 'Transs-Hotel-San-Vicente-', 'releaseID': '4625982', 'have': '16', 'want': '112'}, 
# {'name': 'Johnnie-Walker-5-And-Jacqueline-Dee-Farewell-To-Welfare', 'releaseID': '4984020', 'have': '30', 'want': '653'}, 
# {'name': 'Ghetto-Brothers-Power-Fuerza', 'releaseID': '2673205', 'have': '60', 'want': '1212'}, 
# {'name': 'Rita-The-Tiaras-Gone-With-The-Wind-Is-My-

