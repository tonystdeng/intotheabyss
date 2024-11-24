import pygame as pg
import random
import sys

def getWH():
    import tkinter as tk
    root=tk.Tk()
    width=int(root.winfo_screenwidth()*0.8)
    height=int(root.winfo_screenheight()*0.8)
    root.destroy()
    del tk
    return width,height

class Main:
    def __init__(self) -> None:
        self.width,self.height=getWH()
        self.hw,self.hh=self.width/2,self.height/2
        self.screct=(self.width,self.height)
        pg.init()
        pg.display.set_caption("")
        self.scr=pg.display.set_mode(self.screct)
        self.clock=pg.time.Clock()
        self.deep=0 # how deep you are into your mind, max 5
        self.dpb=1 # how many background does it take you deeper
        self.walk_speed=self.width/128
        pg.font.init()  
        self.assets=self.load()
        self.status="walk" # "attack", "w2a", "a2w"
        self.w2a=0
        self.yforce=0
        self.y=0
        self.targets=[] # list of pos for bullets to go to
        self.fpa=12 # frame per animation (20 ms)
        self.dire=False
        self.walking=0
        self.nwc=self.fpa # stands for next_walk_countdown
        self.healthes=[100,100]
        self.playerposes=[]
        self.front_page()

    def load(self):
        self.pixel_rate=round(self.height/4/pg.image.load(f"assets/image/updown0.png").get_height())
        assets={
            "img":{
                "updown":10,
                "resizeattack":11,
                "attack": 7,
                "nerve":-1,
                "intro":-1,
                "boss":-1,
                "bullet":2,
                "bossfall":-1,
                "playerfall":-1,
                "plane":-1,
                "knife":-1,
                "mental":-1
            },
            "fonts":{
                "GomePixel":6,
                "Stepalange":8,
                "Stepalange0":24
            }
        }
        for i in assets["img"]:
            if assets["img"][i]<0:
                img=pg.image.load(f"assets/image/{i}.png")
                img=pg.transform.scale_by(img,self.pixel_rate)
                assets["img"][i]=img
                continue
            list0=[]
            for index in range(assets["img"][i]):
                img=pg.image.load(f"./assets/image/{i}{index}.png")
                img=pg.transform.scale_by(img,self.pixel_rate)
                list0.append(img)
            assets["img"][i]=list0
        for i in assets["fonts"]:
            assets["fonts"][i]=pg.font.Font(f"assets/fonts/{i}.otf",int(self.height/assets["fonts"][i]))
        return assets

    def generate_map(self,front=None):
        base=pg.Surface((self.width,self.height/6))
        base.fill((200,0,0))
        for x in range(round(self.width/self.pixel_rate)):
            for y in range(round(base.get_width()/self.pixel_rate)):
                if not random.randint(0,int(y/(self.deep+1))):
                    base.fill((100,0,0),(x*self.pixel_rate,y*self.pixel_rate,self.pixel_rate,self.pixel_rate))
        if not front:
            nerves=[[],[]]#(co,sur)
        else:
            nerves=[*front[:],[]]
        for i in range(10):
            nerve=self.assets["img"]["nerve"].copy()
            nerve=pg.transform.scale_by(nerve,1-random.randint(0,5)/10)
            nerve=pg.transform.flip(nerve,random.randint(0,1),random.randint(0,1))
            nerve=pg.transform.rotate(nerve,random.randint(0,360))
            nerve.set_alpha(random.randint(0,128))
            co=(random.randint(0,self.width),random.randint(0,self.height))
            nerves[1].append([nerve,co]) 
        return [nerves,base] #([(img,co),],img) 
    
    def displaybg(self,bg0,bg1,num):
        x=-1
        for nerves in bg1[0]:
            for nerve in nerves:
                self.scr.blit(nerve[0],(nerve[1][0]+num+self.width*x,nerve[1][1]))
            x+=1
        for x,bg in ((num,bg0),(num+self.width,bg1)):
            self.scr.blit(bg[1],(x,self.height-bg[1].get_height()))
    
    def front_page_font(self,title:pg.Surface,play:pg.Surface,play_touched:pg.Surface):
        rect0=title.get_rect()
        rect0.centerx=self.hw
        rect0.y=rect0.h
        self.scr.blit(title,rect0)
        rect1=play.get_rect()
        rect1.centerx=self.hw
        rect1.y=rect1.h+rect0.h*2
        if rect1.collidepoint(pg.mouse.get_pos()):
            self.scr.blit(play_touched,rect1)
        else:
            self.scr.blit(play,rect1)
        return rect1


    def front_page(self):
        run=1
        bgs=[]
        bgs.append(self.generate_map())
        for i in range(2):
            bg=self.generate_map(bgs[i][0][-2:])
            bgs.append(bg)
        bg_walk=0
        walking=0
        nwc=self.fpa # stands for next_walk_countdown
        title=self.assets["fonts"]["GomePixel"].render("INTO THE ABYSS",False,(150,0,0))
        play=self.assets["fonts"]["Stepalange"].render("Play",False,(150,0,0))
        play_touched=self.assets["fonts"]["Stepalange"].render("Play",False,(255,0,0))
        while run:
            self.scr.fill((40+self.deep*10,40,0))
            self.displaybg(bgs[0],bgs[1],bg_walk)
            # remove old bg and add new
            bg_walk-=self.walk_speed/2
            if -bg_walk>self.width:
                bg_walk+=self.width
                del bgs[0]
                bgs.append(self.generate_map(bgs[-1][0][-2:]))
            nwc-=1
            if not nwc:
                walking+=1
                nwc=self.fpa
            if walking>len(self.assets["img"]["updown"])-1:
                walking=0
            rect:pg.Rect=self.assets["img"]["updown"][walking].get_rect()
            rect.centerx=self.width*0.25
            rect.bottom=self.height-self.height/6
            self.scr.blit(self.assets["img"]["updown"][walking],rect)
            button=self.front_page_font(title,play,play_touched)
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                if e.type==pg.MOUSEBUTTONDOWN:
                    if button.collidepoint(pg.mouse.get_pos()):
                        if self.intro():
                            self.main()
                            self.__init__()
            pg.display.flip()
            self.clock.tick(60)
            pg.display.set_caption(str(self.clock.get_fps()))
    
    def intro(self):
        self.pause=self.assets["fonts"]["Stepalange"].render("Pause",False,(255,0,0))
        self.pause_touched=self.assets["fonts"]["Stepalange"].render("Pause",False,(150,0,0))
        introdio=["you are born to help him","but you are not yet informed enough","go see it your self","(click to proceed)"]
        intro_font=self.makedio(introdio,True)
        img=self.assets["img"]["intro"]
        img=pg.transform.scale(img,self.screct)
        while True:
            self.scr.blit(img,(0,0))
            button=self.play_font([[intro_font,10]])
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                elif e.type==pg.MOUSEBUTTONDOWN:
                    if button.collidepoint(pg.mouse.get_pos()):
                        return False
                    else:
                        return True
            pg.display.flip()

    def makedio(self,dio,dark=False):
        returns=[]
        for i in dio:
            font=self.assets["fonts"]["Stepalange0"].render(i,False,(255,0,0) if dark else(255,255,255))
            returns.append(font)
        return returns

    def play_font(self,dialogs=None):
        rect1=self.pause.get_rect()
        rect1.x=rect1.h
        rect1.y=rect1.h/2
        if rect1.collidepoint(pg.mouse.get_pos()):
            self.scr.blit(self.pause,rect1)
        else:
            self.scr.blit(self.pause_touched,rect1)
        if dialogs:# [[font,countdown]...]
            index=0
            for i in dialogs:
                if i[1]<0:
                    dialogs.remove(i)
                    continue
                i[1]-=1
                for j in i[0]:
                    rect0=j.get_rect()
                    rect0.centerx=self.hw
                    rect0.y=(index*2+4)*rect0.h
                    self.scr.blit(j,rect0)
                    index+=1
                index+=1
        return rect1

    def player_move(self,xchange=0,enemyrect=None):
        shot=None
        if self.status=="walk":
            self.nwc-=1
            if not self.nwc:
                self.walking+=1
                self.nwc=self.fpa
                if self.walking==len(self.assets["img"]["updown"]):
                    self.walking=0
            rect=self.assets["img"]["updown"][self.walking].get_rect()
            rect.centerx=self.width/2+xchange
            img=self.assets["img"]["updown"][self.walking]
        elif self.status=="w2a":
            self.w2a+=1
            if self.w2a==len(self.assets["img"]["resizeattack"]):
                self.w2a-=1
                self.status="attack"
            rect=self.assets["img"]["resizeattack"][self.w2a].get_rect()
            rect.centerx=self.width/2+xchange-rect.w/4*2*(self.dire-0.5)
            img=self.assets["img"]["resizeattack"][self.w2a] 
        elif self.status=="attack":
            rect=self.assets["img"]["resizeattack"][-1].get_rect()
            rect.centerx=self.width/2+xchange-rect.w/4*2*(self.dire-0.5)
            rect.bottom=self.height-self.height/6
            candelespos=list(rect.center)
            candelespos[0]-=2*(self.dire-0.5)*rect.w/5
            candelespos[1]-=rect.h/5
            shot=self.shot(candelespos)
            img=self.assets["img"]["resizeattack"][-1]
        elif self.status=="a2w":
            self.w2a-=1
            if self.w2a<0:
                self.w2a+=1
                self.status="walk"
            rect=self.assets["img"]["resizeattack"][self.w2a].get_rect()
            rect.centerx=self.width/2+xchange-rect.w/4*2*(self.dire-0.5)
            img=self.assets["img"]["resizeattack"][self.w2a] 

        self.y+=self.yforce
        if self.y<=0:
            self.y=0
            self.yforce=0
        else:
            self.yforce-=1
        rect.bottom=self.height-self.height/6-self.y
        self.scr.blit(pg.transform.flip(img,self.dire,False),rect)
        self.scr.fill((0,0,200),(rect.x,rect.y-rect.h/20,
                                     rect.w/100*self.healthes[0],rect.h/20))
        self.playerposes.append(rect)
        if len(self.playerposes)>20:
            del self.playerposes[0]
        if shot and enemyrect:
            if enemyrect.collidepoint(shot):
                self.healthes[-1]-=10


    def shot(self,candeles):
        self.nwc-=1
        if not self.nwc:
            self.nwc=self.fpa
            if len(self.targets):
                pos=self.targets[0]
                if pos[0]>candeles[1]:
                    self.dire=False
                else:self.dire=True
                self.targets.remove(pos)
                pg.draw.line(self.scr,(255,255,255),candeles,pos,round(self.height/64))
                return pos

    def control(self):
        x_change=0
        keys=pg.key.get_pressed()
        if keys[pg.K_a] or keys[pg.K_LEFT]:
            x_change-=self.walk_speed
            self.dire=True
        if keys[pg.K_d] or keys[pg.K_RIGHT]:
            x_change+=self.walk_speed
            self.dire=False
        if keys[pg.K_SPACE] or keys[pg.K_UP]:
            if self.y==0:
                self.yforce=20
            if self.status=="attack" or self.status=="w2a":
                self.status="a2w"
                self.targets.clear()
                
        return x_change

    def main(self):
        run=1
        bgs=[]
        bgs.append(self.generate_map())
        for i in range(2):
            bg=self.generate_map(bgs[i][0][-2:])
            bgs.append(bg)
        bg_walk=0
        bg_change=0
        bg_countdown=self.dpb
        stop_fonts_dio=("Are you afraid of what you're seeing already?","If only you had a way back my son, but you don't...")
        stop_fonts=self.makedio(stop_fonts_dio)
        dialogs=[]
        while run:
            self.scr.fill((40+self.deep*10,40,0))
            self.displaybg(bgs[0],bgs[1],bg_walk)
            bg_walk+=bg_change
            bg_change=0
            if -bg_walk>self.width:
                bg_walk+=self.width
                del bgs[0]
                bgs.append(self.generate_map(bgs[-1][0][-2:]))
                bg_countdown-=1
                if bg_countdown<=0:
                    if self.deep>=5:
                        self.boss_fight_intro(bgs[0],bgs[1])
                        return
                    bg_countdown=self.dpb
                    self.deep+=1
            elif bg_walk>self.hw:
                got=False
                for i in dialogs:
                    if i[0]==stop_fonts:
                        i[1]=120
                        got=True
                        break
                if not got:
                    dialogs.append([stop_fonts,120])
                bg_walk=self.hw*0.9
            self.player_move()
            button=self.play_font(dialogs)
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                elif e.type==pg.MOUSEBUTTONDOWN:
                    if button.collidepoint(pg.mouse.get_pos()):
                        return
                    elif self.status=="walk":
                        self.status="w2a"
                        self.targets.append(pg.mouse.get_pos())
                    elif self.status=="w2a" or self.status=="attack":
                        self.targets.append(pg.mouse.get_pos())
            if self.status=="walk" or self.status=="attack":
                bg_change-=self.control()
            pg.display.flip()
            self.clock.tick(60)
            pg.display.set_caption(str(self.clock.get_fps()))

    def boss_fight_intro(self,bg0,bg1):
        run=1
        bossdios=[(("i though about it but,","i didn't expect for something like you would be here"),300),
                 (("why, why is he trying to stop me,"," i can make this place not like hell again"),300),
                 (("but no worries, i won't let you stop me",),150)]
        boss_fonts=[]
        for i,time in bossdios:
            boss_fonts.append([self.makedio(i),time])
        dialogsindex=0
        dialogs=[boss_fonts[dialogsindex]]
        bossimg=self.assets["img"]["boss"]
        bossrect:pg.Rect=bossimg.get_rect()
        bossrect.centerx=self.width*0.75
        bossrect.y=self.height
        decendspeed=2
        stage=0
        attack=0
        while run:
            self.scr.fill((40+self.deep*10,40,0))
            self.displaybg(bg0,bg1,0)

            self.player_move()

            if not stage:
                bossrect.y-=decendspeed
                self.scr.blit(bossimg,bossrect)
                if bossrect.bottom<=self.height-self.height/6:
                    stage=1
            else:
                attack+=1
                if attack==len(self.assets["img"]["attack"]):
                    break
                bossrect=self.assets["img"]["attack"][attack].get_rect()
                bossrect.centerx=self.width*0.75
                bossrect.bottom=self.height-self.height/6
                bossimg=self.assets["img"]["attack"][attack]
                self.scr.blit(bossimg,bossrect)

            if dialogs[-1][1]==0:
                dialogsindex+=1
                if dialogsindex>=3:
                    continue
                dialogs.append(boss_fonts[dialogsindex])

            button=self.play_font(dialogs)
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                elif e.type==pg.MOUSEBUTTONDOWN:
                    if button.collidepoint(pg.mouse.get_pos()):
                        return
                self.control()
            pg.display.flip()
            self.clock.tick(60)
            pg.display.set_caption(str(self.clock.get_fps()))
        self.boss_fight(bg0,bg1,bossimg,bossrect)


    def boss_fight(self,bg0,bg1,bossimg,bossrect):
        run=1
        xchage=0
        while run:
            self.scr.fill((40+self.deep*10,40,0))
            self.displaybg(bg0,bg1,0)
            self.player_move(xchage,bossrect)

            self.scr.blit(bossimg,bossrect)
            self.scr.fill((0,0,200),(bossrect.x,bossrect.y-bossrect.h/20,
                                     bossrect.w/100*self.healthes[-1],bossrect.h/20))
            if self.nwc==self.fpa:
                x=bossrect.centerx-bossrect.w/5
                y=bossrect.centery-bossrect.h/5
                pg.draw.line(self.scr,(0,0,200),(x,y),self.playerposes[0].center,round(self.height/32))
                if self.playerposes[-1].collidepoint(self.playerposes[0].center):
                    self.healthes[0]-=20

            button=self.play_font()
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                elif e.type==pg.MOUSEBUTTONDOWN:
                    if button.collidepoint(pg.mouse.get_pos()):
                        return
                    elif self.status=="walk":
                        self.status="w2a"
                        self.targets.append(pg.mouse.get_pos())
                    elif self.status=="w2a" or self.status=="attack":
                        self.targets.append(pg.mouse.get_pos())
            if self.status=="walk" or self.status=="attack":
                xchage+=self.control()
            if xchage>self.hw:xchage=self.hw
            elif xchage<-self.hw:xchage=-self.hw
            if self.healthes[0]<=0:
                self.defeat(self.assets["img"]["playerfall"],self.playerposes[-1],(bossrect.x,bossrect.y),bg0,bg1)
                return
            elif self.healthes[1]<=0:
                self.win(self.assets["img"]["updown"][0],self.playerposes[-1],(bossrect.x,bossrect.y),bg0,bg1)
                return
            pg.display.flip()
            self.clock.tick(60)
            pg.display.set_caption(str(self.clock.get_fps()))

    def defeat(self,playerimg, playerrect,bosscor,bg0,bg1):
        bossdios=[[["my wife was mudered, i wanna revenge", "i wanna kill that man, he murdered my wife"], 300],
        [["but killing is wrong, so my kindness went against it"],200], 
        [["so you were created my son, you are here to replace me","you will have a new life, without hate"],300],
        [["do you wanna revenge for your wife, my copy?"], 150],
        [["right key for yes, left key for no"],10000000000000000000000000000000000000000000000000000000000]]
        boss_fonts=[]
        for i,time in bossdios:
            boss_fonts.append([self.makedio(i),time])
        dialogsindex=0
        dialogs=[boss_fonts[dialogsindex]]
        bossimg=self.assets["img"]["boss"]
        bossrect:pg.Rect=bossimg.get_rect()
        bossrect.x=bosscor[0]
        bossrect.y=bosscor[1]
        while True:
            self.scr.fill((40+self.deep*10,40,0))
            self.displaybg(bg0,bg1,0)

            self.scr.blit(bossimg,bossrect)
            self.scr.blit(playerimg,playerrect)

            if dialogs[-1][1]==0:
                dialogsindex+=1
                dialogs.append(boss_fonts[dialogsindex])
            
            self.play_font(dialogs)
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
            keys=pg.key.get_pressed()
            if keys[pg.K_a] or keys[pg.K_LEFT]:
                self.endkill()
                return
            elif keys[pg.K_d] or keys[pg.K_RIGHT]:
                self.endmental()
                return
            pg.display.flip()
            self.clock.tick(60)
            pg.display.set_caption(str(self.clock.get_fps()))
        
    def endmental(self):
        introdio=["you guys started to fight for control",
                  "sometime its a wholesome guy, sometime its a guy",
                  "that just yalls the nameof a person that killed his wife",
                  "soon you guys got sent to the mental hospital, for obvious reasons"]
        intro_font=self.makedio(introdio,True)
        img=self.assets["img"]["mental"]
        img=pg.transform.scale(img,self.screct)
        while True:
            self.scr.blit(img,(0,0))
            self.play_font([[intro_font,10]])
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                elif e.type==pg.MOUSEBUTTONDOWN:
                    return
            pg.display.flip()

    def endkill(self):
        introdio=["well that's not school friendly"]
        intro_font=self.makedio(introdio,True)
        img=self.assets["img"]["knife"]
        img=pg.transform.scale(img,self.screct)
        while True:
            self.scr.blit(img,(0,0))
            self.play_font([[intro_font,10]])
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                elif e.type==pg.MOUSEBUTTONDOWN:
                    return
            pg.display.flip()


    def win(self,playerimg, playerrect,bosscor,bg0,bg1):
        run=1
        bossdios=[(("no.. you even don't understand","if you do, you will do the same thing as me"),300),
                 (("he says he is trying to project you","but he is just trying to follow his old rules!"),300),
                 (("why! why!",),150)]
        boss_fonts=[]
        for i,time in bossdios:
            boss_fonts.append([self.makedio(i),time])
        dialogsindex=0
        dialogs=[boss_fonts[dialogsindex]]
        bossimg=self.assets["img"]["bossfall"]
        bossrect:pg.Rect=bossimg.get_rect()
        bossrect.x=bosscor[0]
        bossrect.y=bosscor[1]
        while run:
            self.scr.fill((40+self.deep*10,40,0))
            self.displaybg(bg0,bg1,0)

            self.scr.blit(bossimg,bossrect)
            self.scr.blit(playerimg,playerrect)

            if dialogs[-1][1]==0:
                dialogsindex+=1
                if dialogsindex>=3:
                    break
                dialogs.append(boss_fonts[dialogsindex])

            self.play_font(dialogs)
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
            pg.display.flip()
            self.clock.tick(60)
            pg.display.set_caption(str(self.clock.get_fps()))

        introdio=["you woked up and found yourself just having a dream",
                  "you know you needs to move to another country to live",
                  "you rememeber that someone you loved seems to be dead?",
                  "na, should be no one important"]
        intro_font=self.makedio(introdio,True)
        img=self.assets["img"]["plane"]
        img=pg.transform.scale(img,self.screct)
        while True:
            self.scr.blit(img,(0,0))
            self.play_font([[intro_font,10]])
            for e in pg.event.get():
                if e.type==pg.QUIT:
                    sys.exit(self)
                elif e.type==pg.MOUSEBUTTONDOWN:
                    return
            pg.display.flip()

Main()
