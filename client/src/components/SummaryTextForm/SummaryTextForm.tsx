import { Button, Textarea, Text } from '@mantine/core';
import { useForm } from '@mantine/form';
import { DangerLevels } from '../DangerLevels/DangerLevels';
import { useSummaryTextForm } from './hooks/useSummaryTextForm';    


export function SummaryTextForm() {
    const form = useForm({
        initialValues: {
            summaryText: '',
        },
        validate: {
            summaryText: (value) => value.length > 0 ? null : 'Summary text is required',
        },
    });
    const { forecast, handleSubmit, summary } = useSummaryTextForm(form.reset);

    return (
        <>
        <form onSubmit={form.onSubmit((values) => handleSubmit(values.summaryText))}>
            <Textarea {...form.getInputProps('summaryText')} />
            <Button variant="filled" color='myColor.5' type="submit">Submit</Button>
        </form>
        {(summary && forecast) && (
            <>
                <Text>{summary}</Text>
                <DangerLevels levels={forecast?.levels || {}} />
            </>
        )}
        </>
    );
}