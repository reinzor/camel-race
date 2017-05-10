<template>
  <div class="site-wrapper">
    <div class="site-wrapper-inner">
        <div class="cover-container" id="app">
            <div class="masthead clearfix">
              <div class="inner">
                <h3 class="masthead-brand">Kamelen Race!</h3>
                <nav>
                  <ul class="nav masthead-nav">
                    <li><a href="#" @click="resetGame">Reset</a></li>
                  </ul>
                </nav>
              </div>
            </div>
            <div class="inner cover">
              <h1 v-if="winner" class="cover-heading">{{winner.name}} wint! - {{minutes}}:{{seconds}}</h1>
              <h1 v-else class="cover-heading">{{minutes}}:{{seconds}}</h1>
              <div v-for="(player, origin, idx) in players" class="player">
                <transition name="fade" mode="out-in">
                  <div class="lastScore"
                    :style="{color: getColor(idx)}"
                    :key="player.lastEvent.time"
                    v-text="player.lastEvent.numPoints" v-if="player.lastEvent"></div>
                </transition>
                <div class="info">
                  <span class="name" v-text="player.name"></span>
                  <span class="score" v-if="winner">- ({{player.score}} punten)</span>
                </div>
                <div class="progress">
                  <div class="progress-bar progress-bar-striped progress-bar-animated"
                    role="progressbar"
                    :style="{width: getPercentage(player.score) + '%', backgroundColor: getColor(idx)}"
                    :aria-valuenow="player.score"
                    aria-valuemin="0"
                    :aria-valuemax="maxScore"></div>
                </div>
              </div>
            </div>
            <div class="mastfoot">
              <div class="inner">
                <p>Kamelen race, <a href="mailto:info@baasvanhorstaandemaas.nl">Baas van Horst aan de Maas</a></p>
              </div>
            </div>
        </div>
    </div>
  </div>
</template>

<script>
function pad (n, width, z) {
  z = z || '0'
  n = n + ''
  return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n
}

var bellAudio = new Audio('static/audio/bell.wav')
bellAudio.pause()
var derbyAudio = new Audio('static/audio/derby.wav')
derbyAudio.pause()
var feelgoodAudio = new Audio('static/audio/feelgood.wav')
feelgoodAudio.pause()

export default {
  name: 'app',
  data () {
    return {
      players: {},
      maxScore: 20,
      startTime: Math.trunc((new Date()).getTime() / 1000),
      sinceStart: 0,
      resetButton: {
        doubleTapTime: 1000,
        count: 0,
        time: null,
        resetGameCount: 1,
        clearPlayersCount: 2
      }
    }
  },
  sockets: {
    connect () {
      console.log('socket connected')
    },
    score (e) {
      // Some logging and add timestamp
      console.log('Score!', e)
      e.time = new Date()

      // Add the player if the origin is not known yet
      if (!(e.origin in this.players)) {
        this.$set(this.players, e.origin, {
          score: 0,
          name: 'Speler ' + (Object.keys(this.players).length + 1),
          lastEvent: null
        })
      }
      // If we do not have a winner, keep track of the points and score the event
      if (!this.winner) {
        this.players[e.origin].score += e.numPoints
        this.players[e.origin].lastEvent = e
      }
    },
    resetGame (e) {
      console.log('resetGame', e)
      this.resetGame()
    }
  },
  computed: {
    winner () {
      for (let origin in this.players) {
        if (this.players[origin].score >= this.maxScore) {
          return this.players[origin]
        }
      }
      return null
    },
    seconds () {
      return pad(this.sinceStart % 60, 2)
    },
    minutes () {
      return pad(parseInt(this.sinceStart / 60) % 60, 2)
    }
  },
  created () {
    window.setInterval(() => {
      if (!this.winner) {
        this.sinceStart = Math.trunc((new Date()).getTime() / 1000) - this.startTime
        if (this.resetButton.time && new Date() - this.resetButton.time > this.resetButton.doubleTapTime) {
          this.resetButton.time = null
          this.resetButton.count = 0
        }
      }
      this.checkAudio()
    }, 100)
  },
  methods: {
    checkAudio () {
      if (this.winner && feelgoodAudio.paused) {
        feelgoodAudio.currentTime = 0
        feelgoodAudio.play()
        derbyAudio.pause()
      }
    },
    getColor (idx) {
      var index = idx % 5
      var colors = ['#5cb85c', '#5bc0de', '#f0ad4e', '#d9534f', '#0275d8']
      return colors[index]
    },
    getPercentage (score) {
      return parseInt(parseFloat(score) / this.maxScore * 100)
    },
    resetGame () {
      feelgoodAudio.pause()
      derbyAudio.currentTime = 0
      derbyAudio.play()
      derbyAudio.addEventListener('ended', () => {
        if (!this.winner) {
          derbyAudio.play()
        }
      })
      bellAudio.currentTime = 0
      bellAudio.play()

      this.resetButton.time = new Date()
      this.resetButton.count += 1
      if (this.resetButton.count >= this.resetButton.clearPlayersCount) {
        this.players = {}
      } else if (this.resetButton.count >= this.resetButton.resetGameCount) {
        for (let origin in this.players) {
          this.players[origin].score = 0
        }

        this.startTime = Math.trunc((new Date()).getTime() / 1000)
      }
    }
  }
}
</script>

<style>
.player {
  padding-bottom: 20px;
  padding-top: 20px;
}

.player .info {
  text-align: left;
}

.player .score {
  color: #d0c1c1
}

.player .lastScore {
  opacity: 0;
  position: absolute;
  margin-left: -20px;
}

.fade-enter {
  opacity: 1 !important;
}
.fade-enter-to {
  transform: scale(10, 10);
}
.fade-enter-active {
  transition: all 1.5s !important;
}
</style>
