axios.defaults.headers.post['Content-Type'] =
  'application/x-www-form-urlencoded';

new Vue({
  el: '#q-app',
  data: function() {
    return {
      login: {
        opened: true,
        captchasrc: '/captcha',
        form: {
          user: '',
          passwd: '',
          captcha: ''
        }
      },
      semesters: [],
      selectedSemester: '',
      firstday: new Date(2019, 1, 25),
      calStyle: ['campus', 'remark', 'teacher'],
      paginationControl: {
        rowsPerPage: 25
      },
      studentInfo: {},
      lessonList: [],
      // schedule: {},
      columns: [
        {
          name: 'kcmc',
          label: '课程名称',
          field: 'kcmc',
          align: 'middle',
          sortable: true
        },
        {
          name: 'kch_id',
          label: '课程编号',
          field: 'kch_id',
          align: 'middle',
          sortable: true
        },
        {
          name: 'jxbmc',
          label: '教学班',
          field: 'jxbmc',
          align: 'middle',
          sortable: true
        },
        {
          name: 'xqmc',
          label: '校区',
          field: 'xqmc',
          align: 'middle',
          sortable: true
        },
        {
          name: 'cdmc',
          label: '教室',
          field: 'cdmc',
          align: 'middle',
          sortable: true
        },
        {
          name: 'xkbz',
          label: '备注',
          field: 'xkbz',
          align: 'middle',
          sortable: true
        },
        {
          name: 'xm',
          label: '教师姓名',
          field: 'xm',
          align: 'middle',
          sortable: true
        },
        {
          name: 'xqj',
          label: '星期',
          field: 'xqj',
          align: 'middle',
          sortable: true
        },
        {
          name: 'jcor',
          label: '节次',
          field: 'jcor',
          align: 'middle',
          sortable: true
        },
        {
          name: 'zcd',
          label: '周次',
          field: 'zcd',
          align: 'middle',
          sortable: true
        }
      ]
    };
  },
  watch: {
    selectedSemester(newval, oldval) {
      if (!oldval.length) return;
      this.$q.loading.show();
      let args = newval.split('-')
      let params = {params: {xnm: args[0], xqm: args[1]}}
      axios
        .get('/data', params)
        .then(resp => {
          console.log(resp);
          if (resp.data.success) {
            console.log(resp.data.data);
            this.studentInfo = resp.data.data.xsxx;
            this.lessonList = resp.data.data.kbList;
          } else {
            this.$q.notify({
              type: 'negative',
              message: resp.data.message,
              position: 'center',
              timeout: 1800
            });
          }
          this.$q.loading.hide();
        })
        .catch(err => {
          let message;
          if (err.response) {
            message = `${err.response.status} - ${err.response.statusText}`;
          }
          this.$q.notify({
            type: 'negative',
            message,
            detail: JSON.stringify(err),
            position: 'top-right'
          });
          console.error(err);
          this.$q.loading.hide();
        });
    }
  },
  computed: {
    TableTitle() {
      const { XNMC, XQMMC, XM } = this.studentInfo;
      return `${XNMC}学年第${XQMMC}学期 ${XM}的课程`;
    },
    DisplayTable() {
      if (!this.login.opened) {
        let table = {};
        if (!this.lessonList.length) return table;
        let data = this.lessonList[0];

        let loc = data.cdmc;
        if (this.calStyle.includes('campus')) {
          loc = `[${data.xqmc}]${data.cdmc}`;
        }

        if (this.calStyle.includes('name@loc')) {
          table.SUMMARY = `${data.kcmc}@${loc}`;
        } else {
          table.SUMMARY = data.kcmc;
          table.LOCATION = loc;
        }

        if (this.calStyle.includes('remark')) {
          if (this.calStyle.includes('teacher')) {
            if (data.xkbz != '无') {
              table.DESCRIPTION = `${data.xm} | ${data.xkbz}`;
            } else {
              table.DESCRIPTION = data.xm;
            }
          } else {
            table.DESCRIPTION = data.xkbz == '无' ? '' : data.xkbz;
          }
        }

        return table;
      }
    },
    DateRange() {
      if (!this.login.opened) {
        let { XNMC } = this.studentInfo;
        let [start, end] = XNMC.split('-');

        return {
          min: new Date(start, 8, 1),
          max: new Date(end, 8, 1)
        };
      } else {
        return {
          min: new Date(2016, 8, 1),
          max: new Date(2025, 8, 1)
        };
      }
    }
  },
  methods: {
    calStyleChange() {
      console.log(this.calStyle);
    },
    CaptchaRefresh() {
      this.login.captchasrc = '/captcha?' + Date.now() + Math.random();
    },
    UpdateSems(sems) {
      let first = true;
      for (let obj of sems) {
        let xxnm = Number(obj.xnm) + 1
        let label =
          (obj.xqm == 3)   ? `${obj.xnm}秋季学期` :
          ((obj.xqm == 12) ? `${xxnm}春季学期` :
                             `${xxnm}小学期`);
        let tmp = {
          label: label,
          value: `${obj.xnm}-${obj.xqm}`
        };
        if (first) {
          first = false;
          this.selectedSemester = tmp.value;
        }
        this.semesters.push(tmp);
      }
    },
    LoginSubmit() {
      if (
        this.login.form.user &&
        this.login.form.passwd &&
        this.login.form.captcha
      ) {
        this.$q.loading.show();
        const params = new URLSearchParams();
        params.append('user', this.login.form.user);
        params.append('passwd', this.login.form.passwd);
        params.append('captcha', this.login.form.captcha);

        axios
          .post('/login', params)
          .then(resp => {
            console.log(resp);
            if (resp.data.success) {
              console.log(resp.data.data);
              this.login.opened = false;
              this.studentInfo = resp.data.data.xsxx;
              this.lessonList = resp.data.data.kbList;
              this.UpdateSems(resp.data.sems);
              // this.schedule = resp.data.data;
            } else {
              this.$q.notify({
                type: 'negative',
                message: resp.data.message,
                position: 'center',
                timeout: 1800
              });
              this.CaptchaRefresh();
              this.login.form.captcha = '';
            }
            this.$q.loading.hide();
          })
          .catch(err => {
            let message;
            if (err.response) {
              message = `${err.response.status} - ${err.response.statusText}`;
            }
            this.$q.notify({
              type: 'negative',
              message,
              detail: JSON.stringify(err),
              position: 'top-right'
            });
            console.error(err);
            this.$q.loading.hide();
          });
      } else {
        this.$q.notify({
          type: 'warning',
          message: '请完整填写表单',
          position: 'center',
          timeout: 1800
        });
        return;
      }
    },
    StyleSubmit() {
      const y = this.firstday.getYear();
      const m = this.firstday.getMonth();
      const d = this.firstday.getDate();
      const firstday = `${y + 1900}/${m + 1}/${d}`;

      console.log(firstday);

      const params = new URLSearchParams();
      params.append('firstday', firstday);
      params.append('style', JSON.stringify(this.calStyle));
      axios
        .post('/post', params, { responseType: 'blob' })
        .then(resp => {
          let blob = new Blob([resp.data], { type: 'text/calendar' });
          let url = window.URL.createObjectURL(blob);
          let link = document.createElement('a');
          link.style.display = 'none';
          link.href = url;
          link.setAttribute('download', this.studentInfo.XH + '.ics');
          document.body.appendChild(link);
          link.click();
        })
        .catch(err => {
          let message;
          if (err.response) {
            message = `${err.response.status} - ${err.response.statusText}`;
          }
          this.$q.notify({
            type: 'negative',
            message,
            detail: JSON.stringify(err),
            position: 'top-right'
          });
          console.error(err);
        });
    }
  }
});
