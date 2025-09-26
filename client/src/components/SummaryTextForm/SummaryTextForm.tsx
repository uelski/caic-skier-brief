import { Button, Textarea } from '@mantine/core';
import { useForm } from '@mantine/form';
import { predictText } from '../../api';
import { useSummaryTextForm } from './hooks/useSummaryTextForm';    


export function SummaryTextForm() {
    const { forecast, handleSubmit } = useSummaryTextForm();
    const form = useForm({
        initialValues: {
            summaryText: '',
        },
    });

    return (
        <form onSubmit={form.onSubmit((values) => handleSubmit(values.summaryText))}>
            <Textarea {...form.getInputProps('summaryText')} />
            <Button type="submit">Submit</Button>
        </form>
    );
}