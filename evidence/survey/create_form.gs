function taoForm4guys() {
  const props = PropertiesService.getUserProperties();
  const id = props.getProperty('survey4guysId');
  if (id) {
    const existing = FormApp.openById(id);
    console.log(existing.getEditUrl(), existing.getPublishedUrl());
    return;
  }
  const form = FormApp.create('Lần gần nhất bạn đặt đồ ăn bị thiếu món (3 phút)');
  form.setCollectEmail(false).setDescription(
    'Nhóm 4guys (AI20K, Track D) đang tìm hiểu chuyện đã xảy ra khi đơn đồ ăn giao tới bị thiếu hoặc sai món.\n' +
    'Khoảng 3 phút. Bạn có thể trả lời ẩn danh bằng cách bỏ trống ô Discord / Zalo ở cuối. Không có câu trả lời đúng sai; không nhớ thì chọn "Không nhớ" nếu có.'
  );
  function choice(title, options) {
    return form.addMultipleChoiceItem().setTitle(title).setChoiceValues(options).setRequired(true);
  }
  const frequency = form.addMultipleChoiceItem().setRequired(true).setTitle('1. Trong 3 tháng qua, bạn đặt đồ ăn / đồ uống giao tới qua app (ShopeeFood, GrabFood, be, Xanh SM...) khoảng bao nhiêu lần?');
  const screening = form.addPageBreakItem().setTitle('Phần 1 · Trải nghiệm đặt món');
  choice('2. Bạn đã từng đặt đồ ăn giao tới bệnh viện chưa (cho mình hoặc người nhà)?', ['Có, trong 3 tháng qua', 'Có, lâu hơn 3 tháng', 'Chưa bao giờ']);
  const issue = form.addMultipleChoiceItem().setRequired(true).setTitle('3. Trong 3 tháng qua, có đơn nào giao tới bị thiếu hoặc sai món (thiếu món, thiếu phần, thiếu ly nước, thiếu topping, nhận nhầm món) không?');
  const details = form.addPageBreakItem().setTitle('Phần 2 · Lần gần nhất đơn bị thiếu / sai món');
  choice('4. Lần gần nhất chuyện đó xảy ra là khi nào?', ['Tuần này', 'Tuần trước', 'Trong tháng này', '1-3 tháng trước']);
  choice('5. Lần đó bạn đặt qua app nào?', ['ShopeeFood', 'GrabFood', 'be', 'Xanh SM', 'Khác']);
  choice('6. Lần đó, phần bị thiếu / sai trị giá khoảng bao nhiêu?', ['Dưới 30k', '30-60k', '60-100k', 'Trên 100k', 'Không nhớ']);
  form.addCheckboxItem().setTitle('7. Lần đó, bạn đã làm gì? (chọn được nhiều)').setRequired(true)
    .setChoiceValues(['Chat với hỗ trợ trong app', 'Gọi tổng đài', 'Nhắn / gọi quán', 'Nhắn / gọi shipper', 'Đánh giá thấp / viết review', 'Không làm gì, bỏ qua']).showOtherOption(true);
  choice('8. Lần đó bạn nói chuyện với ai?', ['Chỉ bot / trả lời tự động', 'Bot rồi tới nhân viên', 'Nhân viên ngay từ đầu', 'Quán / shipper', 'Không liên hệ ai']);
  choice('9. Từ lúc bắt đầu khiếu nại đến khi có kết quả (hoặc bạn bỏ cuộc) mất khoảng bao lâu?', ['Không khiếu nại', 'Dưới 5 phút', '5-15 phút', '15-60 phút', 'Hơn 1 tiếng', 'Hơn 1 ngày', 'Vẫn chưa xong']);
  choice('10. Kết quả cuối cùng của lần đó là gì?', ['Được hoàn đúng giá phần thiếu (tiền hoặc ví)', 'Được giao bù đúng món', 'Chỉ được mã giảm giá / voucher / xu', 'Được hoàn một phần', 'Không được gì', 'Đang chờ, chưa xong', 'Không khiếu nại']);
  const end = form.addPageBreakItem().setTitle('Phần 3 · Chia sẻ thêm');
  form.addParagraphTextItem().setTitle('11. Điều gì khó chịu nhất ở lần đó (hoặc lần gần nhất bạn khiếu nại một đơn đồ ăn)?').setRequired(false);
  form.addTextItem().setTitle('12. Nếu sẵn lòng cho nhóm hỏi thêm 10 phút về lần đó, để lại Discord / Zalo.').setRequired(false);
  frequency.setChoices(['0 lần', '1-3 lần', '4-10 lần', 'Hơn 10 lần'].map((v, i) => frequency.createChoice(v, i === 0 ? end : screening)));
  issue.setChoices(['Có, thiếu món', 'Có, sai món', 'Có, cả hai', 'Không', 'Không nhớ'].map((v, i) => issue.createChoice(v, i < 3 ? details : end)));
  props.setProperty('survey4guysId', form.getId());
  console.log(form.getEditUrl(), form.getPublishedUrl());
}
