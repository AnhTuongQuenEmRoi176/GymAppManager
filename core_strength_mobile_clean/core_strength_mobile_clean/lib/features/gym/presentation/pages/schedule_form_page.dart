import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../../core/theme/app_colors.dart';
import '../../../../core/theme/app_layout.dart';
import '../../../../core/utils/formatters.dart';
import '../../../../core/widgets/app_card.dart';
import '../../../../core/widgets/page_state.dart';
import '../../domain/entities/gym_entities.dart';
import '../providers/gym_providers.dart';

class ScheduleFormPage extends ConsumerStatefulWidget {
  const ScheduleFormPage({super.key, this.existing});

  final TrainingSession? existing;

  bool get isEditing => existing != null;

  @override
  ConsumerState<ScheduleFormPage> createState() => _ScheduleFormPageState();
}

class _ScheduleFormPageState extends ConsumerState<ScheduleFormPage> {
  final _formKey = GlobalKey<FormState>();
  late final TextEditingController _titleController;
  late final TextEditingController _locationController;
  late final TextEditingController _noteController;

  int? _memberId;
  int? _memberPackageId;
  late DateTime _startAt;
  late DateTime _endAt;
  bool _saving = false;

  @override
  void initState() {
    super.initState();
    final existing = widget.existing;
    final now = DateTime.now();
    final defaultStart = DateTime(now.year, now.month, now.day + 1, 18);

    _titleController = TextEditingController(text: existing?.title ?? '');
    _locationController = TextEditingController(text: existing?.location ?? '');
    _noteController = TextEditingController(text: existing?.note ?? '');
    _startAt = existing?.startAt ?? defaultStart;
    _endAt = existing?.endAt ?? defaultStart.add(const Duration(hours: 1));
  }

  @override
  void dispose() {
    _titleController.dispose();
    _locationController.dispose();
    _noteController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isEditing ? 'Sửa lịch dạy' : 'Tạo lịch dạy'),
      ),
      body: SafeArea(
        child: Form(
          key: _formKey,
          child: ListView(
            padding: const EdgeInsets.fromLTRB(
              AppLayout.pagePadding,
              18,
              AppLayout.pagePadding,
              30,
            ),
            children: [
              AppCard(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.isEditing ? 'Thông tin buổi dạy' : 'Xếp lịch với hội viên',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 5),
                    Text(
                      widget.isEditing
                          ? 'Bạn có thể đổi nội dung, ngày giờ và địa điểm của lịch.'
                          : 'Chỉ những hội viên đang có gói PT của bạn mới xuất hiện.',
                      style: Theme.of(context).textTheme.bodySmall,
                    ),
                    const SizedBox(height: 18),
                    if (widget.isEditing)
                      TextFormField(
                        initialValue: widget.existing!.participantName,
                        readOnly: true,
                        decoration: const InputDecoration(
                          labelText: 'Hội viên',
                          prefixIcon: Icon(Icons.person_outline_rounded),
                        ),
                      )
                    else
                      _buildMemberField(),
                    const SizedBox(height: 14),
                    TextFormField(
                      controller: _titleController,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Nội dung buổi tập *',
                        hintText: 'Ví dụ: Tập ngực - vai',
                        prefixIcon: Icon(Icons.fitness_center_rounded),
                      ),
                      validator: (value) {
                        final text = value?.trim() ?? '';
                        if (text.isEmpty) return 'Hãy nhập nội dung buổi tập.';
                        if (text.length < 2) return 'Nội dung quá ngắn.';
                        return null;
                      },
                    ),
                    const SizedBox(height: 14),
                    _DateTimeField(
                      label: 'Bắt đầu',
                      value: _startAt,
                      onTap: () => _pickDateTime(isStart: true),
                    ),
                    const SizedBox(height: 14),
                    _DateTimeField(
                      label: 'Kết thúc',
                      value: _endAt,
                      onTap: () => _pickDateTime(isStart: false),
                    ),
                    const SizedBox(height: 14),
                    TextFormField(
                      controller: _locationController,
                      textInputAction: TextInputAction.next,
                      decoration: const InputDecoration(
                        labelText: 'Địa điểm',
                        hintText: 'Ví dụ: Khu PT tầng 2',
                        prefixIcon: Icon(Icons.place_outlined),
                      ),
                    ),
                    const SizedBox(height: 14),
                    TextFormField(
                      controller: _noteController,
                      minLines: 3,
                      maxLines: 5,
                      decoration: const InputDecoration(
                        labelText: 'Ghi chú',
                        hintText: 'Mục tiêu hoặc lưu ý cho buổi tập',
                        alignLabelWithHint: true,
                        prefixIcon: Padding(
                          padding: EdgeInsets.only(bottom: 52),
                          child: Icon(Icons.notes_rounded),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: _saving ? null : _save,
                icon: _saving
                    ? const SizedBox(
                        width: 18,
                        height: 18,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                          color: Colors.white,
                        ),
                      )
                    : const Icon(Icons.check_rounded),
                label: Text(_saving
                    ? 'Đang lưu...'
                    : widget.isEditing
                        ? 'Lưu thay đổi'
                        : 'Tạo lịch'),
              ),
              const SizedBox(height: 10),
              OutlinedButton(
                onPressed: _saving ? null : () => Navigator.of(context).pop(false),
                child: const Text('Hủy'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMemberField() {
    final asyncMembers = ref.watch(assignedMembersProvider);
    return asyncMembers.when(
      loading: () => const SizedBox(
        height: 58,
        child: Center(child: CircularProgressIndicator(strokeWidth: 2)),
      ),
      error: (error, _) => ErrorState(
        message: error.toString(),
        onRetry: () => ref.invalidate(assignedMembersProvider),
      ),
      data: (members) {
        if (members.isEmpty) {
          return Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: AppColors.warningSoft,
              borderRadius: BorderRadius.circular(AppLayout.controlRadius),
              border: Border.all(color: AppColors.warningBorder),
            ),
            child: const Row(
              children: [
                Icon(Icons.info_outline_rounded, color: AppColors.warning),
                SizedBox(width: 10),
                Expanded(
                  child: Text(
                    'Bạn chưa có hội viên nào đang sử dụng gói PT.',
                    style: TextStyle(
                      color: AppColors.textPrimary,
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              ],
            ),
          );
        }

        return DropdownButtonFormField<int>(
          value: _memberId,
          isExpanded: true,
          decoration: const InputDecoration(
            labelText: 'Hội viên *',
            prefixIcon: Icon(Icons.person_outline_rounded),
          ),
          items: members
              .map(
                (member) => DropdownMenuItem<int>(
                  value: member.id,
                  child: Text(
                    '${member.fullName} • còn ${member.sessionsRemaining} buổi',
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              )
              .toList(),
          onChanged: (value) {
            if (value == null) return;
            final member = members.firstWhere((item) => item.id == value);
            setState(() {
              _memberId = member.id;
              _memberPackageId = member.memberPackageId;
            });
          },
          validator: (value) => value == null ? 'Hãy chọn hội viên.' : null,
        );
      },
    );
  }

  Future<void> _pickDateTime({required bool isStart}) async {
    final current = isStart ? _startAt : _endAt;
    final date = await showDatePicker(
      context: context,
      initialDate: current,
      firstDate: DateTime.now().subtract(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 730)),
    );
    if (date == null || !mounted) return;

    final selectedTime = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.fromDateTime(current),
    );
    if (selectedTime == null || !mounted) return;

    final value = DateTime(
      date.year,
      date.month,
      date.day,
      selectedTime.hour,
      selectedTime.minute,
    );

    setState(() {
      if (isStart) {
        final oldDuration = _endAt.difference(_startAt);
        _startAt = value;
        _endAt = value.add(
          oldDuration.isNegative || oldDuration == Duration.zero
              ? const Duration(hours: 1)
              : oldDuration,
        );
      } else {
        _endAt = value;
      }
    });
  }

  Future<void> _save() async {
    FocusScope.of(context).unfocus();
    if (!(_formKey.currentState?.validate() ?? false)) return;

    if (!widget.isEditing && (_memberId == null || _memberPackageId == null)) {
      _showMessage('Hãy chọn hội viên và gói PT hợp lệ.');
      return;
    }
    if (!_endAt.isAfter(_startAt)) {
      _showMessage('Thời gian kết thúc phải sau thời gian bắt đầu.');
      return;
    }
    if (_startAt.isBefore(DateTime.now())) {
      _showMessage('Không thể tạo hoặc chuyển lịch sang thời điểm đã qua.');
      return;
    }

    setState(() => _saving = true);
    try {
      final repository = ref.read(gymRepositoryProvider);
      if (widget.isEditing) {
        await repository.updateSchedule(
          widget.existing!.id,
          ScheduleUpdateInput(
            title: _titleController.text.trim(),
            startAt: _startAt,
            endAt: _endAt,
            location: _locationController.text,
            note: _noteController.text,
          ),
        );
      } else {
        await repository.createSchedule(
          ScheduleCreateInput(
            memberId: _memberId!,
            memberPackageId: _memberPackageId!,
            title: _titleController.text.trim(),
            startAt: _startAt,
            endAt: _endAt,
            location: _locationController.text,
            note: _noteController.text,
          ),
        );
      }

      if (!mounted) return;
      Navigator.of(context).pop(true);
    } catch (error) {
      if (!mounted) return;
      _showMessage(error.toString());
    } finally {
      if (mounted) setState(() => _saving = false);
    }
  }

  void _showMessage(String message) {
    ScaffoldMessenger.of(context)
      ..hideCurrentSnackBar()
      ..showSnackBar(SnackBar(content: Text(message)));
  }
}

class _DateTimeField extends StatelessWidget {
  const _DateTimeField({
    required this.label,
    required this.value,
    required this.onTap,
  });

  final String label;
  final DateTime value;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(AppLayout.controlRadius),
      child: InputDecorator(
        decoration: InputDecoration(
          labelText: label,
          prefixIcon: const Icon(Icons.event_outlined),
          suffixIcon: const Icon(Icons.edit_calendar_outlined),
        ),
        child: Text(
          '${AppFormatters.date.format(value)} • ${AppFormatters.time.format(value)}',
          style: const TextStyle(
            color: AppColors.textPrimary,
            fontSize: 14,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    );
  }
}
